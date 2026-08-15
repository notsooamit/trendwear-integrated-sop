"""
TrendWear S&OP Financial Rollup & Gross Margin Engine
Calculates Revenue, Material COGS, Logistics, Markdown Erosion, and Waterfall Margins.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from .data_loader import DataLoader, OUTPUT_DIR


class FinancialEngine:
    def __init__(self, loader: DataLoader):
        self.loader = loader

    def calculate_financials(self, demand_df: pd.DataFrame = None, opt_df: pd.DataFrame = None, mark_df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Rolls up full S&OP Financial Waterfall:
        Gross Revenue - Material COGS - Logistics Freight - Markdown Loss = Gross Margin ($ / %)
        """
        if demand_df is None:
            demand_df = self.loader.seasonal_demand
        if opt_df is None:
            from .optimizer import SourcingOptimizer
            opt_df = SourcingOptimizer(self.loader).optimize_procurement()
        if mark_df is None:
            from .markdown_engine import MarkdownEngine
            mark_df = MarkdownEngine(self.loader).evaluate_sell_through_and_markdowns()

        sku_m = self.loader.sku_master

        # 1. Gross Revenue
        merged_dem = demand_df.merge(sku_m[["sku_id", "unit_retail_price"]], on="sku_id", how="left")
        total_demand_units = int(merged_dem["forecasted_demand_units"].sum())
        gross_revenue = round((merged_dem["forecasted_demand_units"] * merged_dem["unit_retail_price"]).sum(), 2)

        # 2. Material COGS (From optimized procurement plan)
        material_cogs = round(opt_df["purchase_cost"].sum(), 2)

        # 3. Logistics Freight Cost
        logistics_df = self.loader.logistics
        avg_freight_per_unit = logistics_df["transportation_cost_per_unit"].mean()
        logistics_cost = round(total_demand_units * avg_freight_per_unit, 2)

        # 4. Markdown Impact / Revenue Erosion
        markdown_erosion = round(
            (mark_df["inventory_value_at_risk"] * mark_df["recommended_discount_pct"]).sum(), 2
        )

        # 5. Net Gross Margin
        net_gross_margin = round(gross_revenue - material_cogs - logistics_cost - markdown_erosion, 2)
        margin_pct = round((net_gross_margin / max(1.0, gross_revenue)) * 100.0, 1)

        # 6. Waterfall breakdown for visualization
        waterfall = [
            {"step": "Gross Revenue", "amount": gross_revenue, "type": "positive"},
            {"step": "Material COGS", "amount": -material_cogs, "type": "negative"},
            {"step": "Logistics & Freight", "amount": -logistics_cost, "type": "negative"},
            {"step": "Markdown Loss", "amount": -markdown_erosion, "type": "negative"},
            {"step": "Net Gross Margin", "amount": net_gross_margin, "type": "total"}
        ]

        return {
            "total_demand_units": total_demand_units,
            "gross_revenue": gross_revenue,
            "material_cogs": material_cogs,
            "logistics_cost": logistics_cost,
            "markdown_erosion": markdown_erosion,
            "net_gross_margin": net_gross_margin,
            "gross_margin_pct": margin_pct,
            "waterfall": waterfall
        }
