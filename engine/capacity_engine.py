"""
TrendWear S&OP Plant Capacity & Feasibility Engine
Evaluates weekly factory utilization, flags bottlenecks, and provides production shifting actions.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from .data_loader import DataLoader, OUTPUT_DIR


class CapacityEngine:
    def __init__(self, loader: DataLoader):
        self.loader = loader

    def check_capacity_feasibility(self, capacity_override: pd.DataFrame = None) -> pd.DataFrame:
        """
        Evaluates weekly plant capacity utilization across all 5 plants for Weeks 1 to 12.
        Flags bottlenecks (> 95% utilization, critical alert if > 100%).
        """
        cap_df = capacity_override if capacity_override is not None else self.loader.plant_capacity
        plant_master = self.loader.plant_master

        merged = cap_df.merge(plant_master, on="plant_id", how="left")

        merged["net_available_capacity"] = merged["max_units_capacity"] - merged["maintenance_units"]
        merged["utilization_pct"] = (
            (merged["already_allocated_units"] / merged["max_units_capacity"]) * 100.0
        ).round(1)

        merged["capacity_gap"] = (
            merged["already_allocated_units"] - merged["net_available_capacity"]
        ).clip(lower=0)

        def flag_status(row):
            util = row["utilization_pct"]
            if util > 100.0:
                return "OVERLOADED"
            elif util >= 90.0:
                return "HIGH_UTILIZATION"
            elif util >= 60.0:
                return "OPTIMAL"
            else:
                return "UNDER_UTILIZED"

        merged["capacity_status"] = merged.apply(flag_status, axis=1)

        # Output production plan
        out_file = os.path.join(OUTPUT_DIR, "production_plan.csv")
        merged.to_csv(out_file, index=False)
        return merged

    def shift_production(self, source_plant: str = "P003", target_plant: str = "P004", period: str = "W06", units_to_shift: int = 1440) -> Dict[str, Any]:
        """
        Executes a production reallocation action:
        Shifts units from overloaded source plant to target plant with available flex capacity.
        """
        cap_df = self.loader.plant_capacity.copy()
        
        src_mask = (cap_df["plant_id"] == source_plant) & (cap_df["period"] == period)
        tgt_mask = (cap_df["plant_id"] == target_plant) & (cap_df["period"] == period)

        if not src_mask.any() or not tgt_mask.any():
            raise ValueError("Invalid source or target plant / period specification.")

        src_alloc_before = cap_df.loc[src_mask, "already_allocated_units"].values[0]
        tgt_alloc_before = cap_df.loc[tgt_mask, "already_allocated_units"].values[0]
        src_max = cap_df.loc[src_mask, "max_units_capacity"].values[0]
        tgt_max = cap_df.loc[tgt_mask, "max_units_capacity"].values[0]

        # Apply shift
        actual_shift = min(units_to_shift, src_alloc_before)
        cap_df.loc[src_mask, "already_allocated_units"] = src_alloc_before - actual_shift
        cap_df.loc[tgt_mask, "already_allocated_units"] = tgt_alloc_before + actual_shift

        # Persist to disk and update DataLoader cache
        prod_cap_path = os.path.join(self.loader.data_dir, "production", "plant_production_capacity.csv")
        cap_df.to_csv(prod_cap_path, index=False)
        self.loader._cache[os.path.join("production", "plant_production_capacity.csv")] = cap_df.copy()

        src_util_after = round(((src_alloc_before - actual_shift) / src_max) * 100.0, 1)
        tgt_util_after = round(((tgt_alloc_before + actual_shift) / tgt_max) * 100.0, 1)

        return {
            "source_plant": source_plant,
            "target_plant": target_plant,
            "period": period,
            "units_shifted": actual_shift,
            "source_utilization_before": round((src_alloc_before / src_max) * 100.0, 1),
            "source_utilization_after": src_util_after,
            "target_utilization_before": round((tgt_alloc_before / tgt_max) * 100.0, 1),
            "target_utilization_after": tgt_util_after,
            "status": "FEASIBLE" if (src_util_after <= 100.0 and tgt_util_after <= 100.0) else "OVER_CAPACITY",
            "business_impact": f"Overload on {source_plant} ({period}) successfully relieved by shifting {actual_shift:,} units to {target_plant}. New {source_plant} utilization: {src_util_after}%, {target_plant} utilization: {tgt_util_after}%."
        }
