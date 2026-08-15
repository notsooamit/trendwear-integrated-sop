"""
TrendWear S&OP In-Season Sell-Through & Markdown Recommender Engine
Tracks velocity, identifies fast/slow movers, flags stock-out risks, and calculates markdown clearance depths.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from .data_loader import DataLoader, OUTPUT_DIR


class MarkdownEngine:
    def __init__(self, loader: DataLoader):
        self.loader = loader

    def evaluate_sell_through_and_markdowns(self) -> pd.DataFrame:
        """
        Processes historical sell-through and current inventory to compute:
        - Sell-Through Rate & Percentiles
        - Weeks of Stock (WOS)
        - Fast / Normal / Slow Mover Classifications
        - Markdown Depth (15%, 25%, 35%, 50%)
        - Stock-out Alerts
        - Capital Value at Risk & Expected Lift
        """
        sell_df = self.loader.historical_sell_through
        inv_df = self.loader.current_inventory
        sku_m = self.loader.sku_master

        # Calculate average sell-through metrics per SKU across recent weeks
        sku_stats = sell_df.groupby("sku_id").agg(
            total_available=("units_available", "sum"),
            total_sold=("units_sold", "sum"),
            mean_sell_through=("sell_through_rate", "mean"),
            avg_weekly_sales=("units_sold", "mean")
        ).reset_index()

        # Total on-hand stock per SKU across all DCs
        tot_inv = inv_df.groupby("sku_id").agg(
            current_on_hand_units=("available_stock_units", "sum"),
            reserved_units=("reserved_stock_units", "sum"),
            safety_threshold=("safety_stock_threshold", "sum"),
            avg_inventory_age=("inventory_age_days", "mean")
        ).reset_index()

        merged = sku_stats.merge(tot_inv, on="sku_id", how="inner").merge(sku_m, on="sku_id", how="inner")

        # Weeks of Stock: CurrentStock / AvgWeeklySales
        merged["weeks_of_stock"] = (
            merged["current_on_hand_units"] / merged["avg_weekly_sales"].clip(lower=1.0)
        ).round(1)

        # Percentile thresholds for classification
        p25 = merged["mean_sell_through"].quantile(0.25)
        p75 = merged["mean_sell_through"].quantile(0.75)

        def classify_mover(st):
            if st >= p75:
                return "FAST_MOVER"
            elif st >= p25:
                return "NORMAL_MOVER"
            else:
                return "SLOW_MOVER"

        merged["mover_class"] = merged["mean_sell_through"].apply(classify_mover)

        # Markdown rules based on WOS & mover class
        def recommend_markdown(row):
            wos = row["weeks_of_stock"]
            m_class = row["mover_class"]

            if m_class == "SLOW_MOVER":
                if wos > 20:
                    return 0.50
                elif wos > 14:
                    return 0.35
                elif wos > 8:
                    return 0.25
                else:
                    return 0.15
            elif m_class == "NORMAL_MOVER" and wos > 16:
                return 0.20
            return 0.0

        merged["recommended_discount_pct"] = merged.apply(recommend_markdown, axis=1)

        # Alerts
        def generate_alert(row):
            m_class = row["mover_class"]
            wos = row["weeks_of_stock"]
            disc = row["recommended_discount_pct"]

            if m_class == "FAST_MOVER" and wos < 4.0:
                return "STOCKOUT_VULNERABILITY_ALERT"
            elif disc >= 0.35:
                return "CRITICAL_EXCESS_INVENTORY"
            elif disc > 0.0:
                return "PROMOTIONAL_MARKDOWN_RECOMMENDED"
            else:
                return "HEALTHY_VELOCITY"

        merged["action_alert"] = merged.apply(generate_alert, axis=1)

        # Financial value at risk & projected clearance lift
        merged["inventory_value_at_risk"] = (
            merged["current_on_hand_units"] * merged["unit_retail_price"]
        ).round(2)

        # Lift multiplier based on historical response
        def compute_lift(disc):
            if disc == 0.50:
                return 2.70
            elif disc == 0.35:
                return 1.95
            elif disc == 0.25:
                return 1.55
            elif disc >= 0.15:
                return 1.25
            return 1.0

        merged["expected_velocity_lift"] = merged["recommended_discount_pct"].apply(compute_lift)
        merged["projected_capital_recovery"] = (
            merged["inventory_value_at_risk"] * (1.0 - merged["recommended_discount_pct"])
        ).round(2)

        out_file = os.path.join(OUTPUT_DIR, "markdown_recommendations.csv")
        merged.to_csv(out_file, index=False)
        return merged
