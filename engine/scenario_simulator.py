"""
TrendWear S&OP What-If Scenario Simulator
Runs live parameter adjustments (Demand Surges, Lead Time Delays, Plant Capacity Drops, Supplier Constraints).
Compares Baseline vs Scenario metrics side-by-side and recommends mitigations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from .data_loader import DataLoader
from .mrp_engine import MRPEngine
from .optimizer import SourcingOptimizer
from .capacity_engine import CapacityEngine
from .markdown_engine import MarkdownEngine
from .financial_engine import FinancialEngine


class ScenarioSimulator:
    def __init__(self, loader: DataLoader):
        self.loader = loader
        self.mrp_engine = MRPEngine(loader)
        self.optimizer = SourcingOptimizer(loader)
        self.capacity_engine = CapacityEngine(loader)
        self.markdown_engine = MarkdownEngine(loader)
        self.financial_engine = FinancialEngine(loader)

    def run_scenario(
        self,
        category: str = "Jackets",
        demand_pct_change: float = 50.0,
        fabric_lead_time_delay_weeks: int = 1,
        plant_p003_capacity_pct: float = 0.0,
        supplier_s004_capacity_pct: float = -30.0
    ) -> Dict[str, Any]:
        """
        Simulates end-to-end impact of custom scenario parameters against Baseline.
        """
        # 1. BASELINE RUN
        base_demand_df = self.loader.seasonal_demand.copy()
        base_mrp = self.mrp_engine.run_netting(base_demand_df)
        base_opt = self.optimizer.optimize_procurement(base_mrp)
        base_cap = self.capacity_engine.check_capacity_feasibility()
        base_mark = self.markdown_engine.evaluate_sell_through_and_markdowns()
        base_fin = self.financial_engine.calculate_financials(base_demand_df, base_opt, base_mark)

        # Baseline summaries
        base_total_demand = int(base_fin["total_demand_units"])
        base_fabric_need = float(round(base_mrp["gross_requirement_meters"].sum(), 2))
        base_p003_util = float(round(base_cap[base_cap["plant_id"] == "P003"]["utilization_pct"].mean(), 1))
        base_overall_util = float(round(base_cap["utilization_pct"].mean(), 1))
        base_proc_cost = float(base_fin["material_cogs"])
        base_gross_margin_pct = float(base_fin["gross_margin_pct"])
        base_risk = "MEDIUM"

        # 2. SCENARIO RUN
        scen_demand_df = base_demand_df.copy()
        sku_m = self.loader.sku_master

        # Apply Category / Overall Demand Shift
        if category == "ALL":
            scen_demand_df["forecasted_demand_units"] = (
                scen_demand_df["forecasted_demand_units"] * (1.0 + demand_pct_change / 100.0)
            ).astype(int)
        else:
            target_skus = sku_m[sku_m["category"] == category]["sku_id"].tolist()
            mask = scen_demand_df["sku_id"].isin(target_skus)
            scen_demand_df.loc[mask, "forecasted_demand_units"] = (
                scen_demand_df.loc[mask, "forecasted_demand_units"] * (1.0 + demand_pct_change / 100.0)
            ).astype(int)

        # Run Scenario MRP
        scen_mrp = self.mrp_engine.run_netting(scen_demand_df)

        # Apply Fabric Lead Time Shock
        if fabric_lead_time_delay_weeks > 0:
            scen_mrp["lead_time_weeks"] = scen_mrp["lead_time_weeks"] + fabric_lead_time_delay_weeks

        # Run Scenario Optimization
        scen_opt = self.optimizer.optimize_procurement(scen_mrp)

        # Apply Plant Capacity Shock
        scen_plant_cap_df = self.loader.plant_capacity.copy()
        if plant_p003_capacity_pct != 0.0:
            p003_mask = scen_plant_cap_df["plant_id"] == "P003"
            scen_plant_cap_df.loc[p003_mask, "max_units_capacity"] = (
                scen_plant_cap_df.loc[p003_mask, "max_units_capacity"] * (1.0 + plant_p003_capacity_pct / 100.0)
            ).astype(int)

        scen_cap = self.capacity_engine.check_capacity_feasibility(scen_plant_cap_df)
        scen_mark = self.markdown_engine.evaluate_sell_through_and_markdowns()
        scen_fin = self.financial_engine.calculate_financials(scen_demand_df, scen_opt, scen_mark)

        # Scenario summaries
        scen_total_demand = int(scen_fin["total_demand_units"])
        scen_fabric_need = float(round(scen_mrp["gross_requirement_meters"].sum(), 2))
        scen_p003_util = float(round(scen_cap[scen_cap["plant_id"] == "P003"]["utilization_pct"].mean(), 1))
        scen_overall_util = float(round(scen_cap["utilization_pct"].mean(), 1))
        scen_proc_cost = float(scen_fin["material_cogs"])
        scen_gross_margin_pct = float(scen_fin["gross_margin_pct"])
        scen_risk = "HIGH" if (scen_p003_util > 100.0 or demand_pct_change > 30.0 or fabric_lead_time_delay_weeks > 1) else "MEDIUM"

        # Generate Actionable S&OP Recommendations
        recommendations = []
        if scen_p003_util > 100.0:
            recommendations.append(f"Plant P003 is overloaded ({scen_p003_util}%). Shift 2,000 units to Plant P004 (flex capacity 20%).")
        if fabric_lead_time_delay_weeks > 0:
            recommendations.append(f"Fabric lead time increased by +{fabric_lead_time_delay_weeks} weeks. Accelerate PO release for FAB_014 immediately.")
        if supplier_s004_capacity_pct < 0:
            recommendations.append("Supplier S004 capacity constrained. Reallocate 25% order volume to S001 and S005.")
        if demand_pct_change >= 40.0:
            recommendations.append("High demand surge: Authorize temporary plant overtime and reserve additional DC freight lanes.")
        if not recommendations:
            recommendations.append("All baseline constraints within healthy tolerances; continue monitoring sell-through.")

        return {
            "parameters": {
                "category": category,
                "demand_pct_change": float(demand_pct_change),
                "fabric_lead_time_delay_weeks": int(fabric_lead_time_delay_weeks),
                "plant_p003_capacity_pct": float(plant_p003_capacity_pct),
                "supplier_s004_capacity_pct": float(supplier_s004_capacity_pct)
            },
            "comparison": {
                "demand_units": {"baseline": base_total_demand, "scenario": scen_total_demand, "delta_pct": float(round(((scen_total_demand - base_total_demand) / max(1, base_total_demand)) * 100, 1))},
                "fabric_requirement_meters": {"baseline": base_fabric_need, "scenario": scen_fabric_need, "delta_pct": float(round(((scen_fabric_need - base_fabric_need) / max(1, base_fabric_need)) * 100, 1))},
                "overall_capacity_utilization_pct": {"baseline": base_overall_util, "scenario": scen_overall_util, "delta": float(round(scen_overall_util - base_overall_util, 1))},
                "plant_p003_utilization_pct": {"baseline": base_p003_util, "scenario": scen_p003_util, "delta": float(round(scen_p003_util - base_p003_util, 1))},
                "procurement_cost": {"baseline": base_proc_cost, "scenario": scen_proc_cost, "delta_pct": float(round(((scen_proc_cost - base_proc_cost) / max(1, base_proc_cost)) * 100, 1))},
                "gross_revenue": {"baseline": float(base_fin["gross_revenue"]), "scenario": float(scen_fin["gross_revenue"]), "delta_pct": float(round(((scen_fin["gross_revenue"] - base_fin["gross_revenue"]) / max(1, base_fin["gross_revenue"])) * 100, 1))},
                "gross_margin_pct": {"baseline": base_gross_margin_pct, "scenario": scen_gross_margin_pct, "delta": float(round(scen_gross_margin_pct - base_gross_margin_pct, 1))},
                "supply_risk_level": {"baseline": base_risk, "scenario": scen_risk}
            },
            "recommended_actions": recommendations
        }
