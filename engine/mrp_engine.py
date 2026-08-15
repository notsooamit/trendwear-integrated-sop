"""
TrendWear S&OP MRP & Material Netting Engine
Handles Demand Aggregation, BOM Explosion, Inventory Netting, and Time-Phased Planning.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from .data_loader import DataLoader, OUTPUT_DIR


class MRPEngine:
    def __init__(self, loader: DataLoader):
        self.loader = loader

    def aggregate_demand(self, demand_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Aggregates regional demand by SKU and Period.
        Output columns: sku_id, period, total_demand_units, mean_confidence
        """
        if demand_df is None:
            demand_df = self.loader.seasonal_demand

        agg_df = demand_df.groupby(["sku_id", "period"]).agg(
            total_demand_units=("forecasted_demand_units", "sum"),
            mean_confidence=("forecast_confidence", "mean")
        ).reset_index()

        # Merge SKU metadata
        sku_m = self.loader.sku_master[["sku_id", "sku_name", "category", "unit_retail_price", "unit_target_margin"]]
        agg_df = agg_df.merge(sku_m, on="sku_id", how="left")
        return agg_df

    def explode_bom(self, agg_demand_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Explodes SKU Demand into Fabric Gross Requirements via BOM.
        RequiredMeters(f, t) = Sum(Demand_SKU(k, t) * FabricPerUnit(k, f) * (1 + WastePct(k, f)))
        """
        if agg_demand_df is None:
            agg_demand_df = self.aggregate_demand()

        bom_df = self.loader.bom_material
        merged = agg_demand_df.merge(bom_df, on="sku_id", how="inner")

        merged["gross_fabric_meters"] = (
            merged["total_demand_units"] * 
            merged["fabric_per_unit_meters"] * 
            (1.0 + merged["waste_pct"])
        ).round(2)

        gross_fab_df = merged.groupby(["fabric_id", "period"]).agg(
            gross_requirement_meters=("gross_fabric_meters", "sum"),
            sku_count=("sku_id", "nunique"),
            total_sku_units=("total_demand_units", "sum")
        ).reset_index()

        return gross_fab_df

    def run_netting(self, demand_override: pd.DataFrame = None) -> pd.DataFrame:
        """
        Performs 6-Week / Multi-Period Time-Phased Material Requirements Planning (MRP).
        Nets Gross Requirement against Opening Inventory, Safety Stock, and Confirmed Receipts.
        """
        agg_demand = self.aggregate_demand(demand_override)
        gross_fabric = self.explode_bom(agg_demand)

        fabric_master = self.loader.fabric_master
        
        # Sort periods in chronological order (W01 to W12, M04 to M06)
        all_periods = sorted(
            gross_fabric["period"].unique(),
            key=lambda x: (0 if x.startswith("W") else 1, int(x[1:]) if x[1:].isdigit() else 99)
        )

        netted_rows = []

        # For each fabric, simulate rolling inventory across periods
        for _, f_row in fabric_master.iterrows():
            fid = f_row["fabric_id"]
            safety_stock = f_row["safety_stock_meters"]
            std_lead_time = f_row["standard_lead_time_weeks"]
            criticality = f_row["criticality"]
            cost_per_meter = f_row["standard_cost_per_meter"]

            # Initialize initial opening inventory (e.g. ~1.5x safety stock)
            # For FAB_014, start with tight initial stock
            if fid == "FAB_014":
                current_on_hand = safety_stock * 0.95
            else:
                current_on_hand = safety_stock * 1.4

            for p in all_periods:
                fab_p_req = gross_fabric[(gross_fabric["fabric_id"] == fid) & (gross_fabric["period"] == p)]
                gross_req = fab_p_req["gross_requirement_meters"].values[0] if len(fab_p_req) > 0 else 0.0

                # Scheduled confirmed receipts from earlier POs
                confirmed_receipts = safety_stock * 0.25 if p in ["W01", "W02"] else 0.0

                total_available = current_on_hand + confirmed_receipts
                
                # Net requirement formula
                net_need = max(0.0, gross_req + safety_stock - total_available)

                # Inventory after demand consumption
                projected_end_inv = max(0.0, total_available - gross_req)
                
                # Inventory coverage in weeks (ratio vs gross requirement)
                inv_coverage_pct = round((total_available / max(1.0, gross_req)) * 100.0, 1)

                netted_rows.append({
                    "fabric_id": fid,
                    "fabric_name": f_row["fabric_name"],
                    "period": p,
                    "gross_requirement_meters": round(gross_req, 2),
                    "opening_inventory_meters": round(current_on_hand, 2),
                    "confirmed_receipts_meters": round(confirmed_receipts, 2),
                    "safety_stock_meters": round(safety_stock, 2),
                    "net_requirement_meters": round(net_need, 2),
                    "projected_ending_inventory": round(projected_end_inv, 2),
                    "inventory_coverage_pct": inv_coverage_pct,
                    "lead_time_weeks": std_lead_time,
                    "criticality": criticality,
                    "standard_cost_per_meter": cost_per_meter,
                    "is_deficit": net_need > 0
                })

                # Carry forward ending inventory + any replenishment
                current_on_hand = projected_end_inv

        df_mrp = pd.DataFrame(netted_rows)
        
        # Save output
        out_file = os.path.join(OUTPUT_DIR, "material_requirements.csv")
        df_mrp.to_csv(out_file, index=False)
        return df_mrp
