"""
TrendWear S&OP Pipeline Orchestrator
Coordinates end-to-end execution of MRP, Optimization, Capacity Feasibility, Markdown Engine, and Financials.
"""

import os
import pandas as pd
from typing import Dict, Any
from .data_loader import DataLoader, OUTPUT_DIR
from .mrp_engine import MRPEngine
from .optimizer import SourcingOptimizer
from .capacity_engine import CapacityEngine
from .markdown_engine import MarkdownEngine
from .financial_engine import FinancialEngine
from .sop_workflow import SOPWorkflowManager
from .scenario_simulator import ScenarioSimulator


class SOPOrchestrator:
    def __init__(self, data_dir: str = None):
        self.loader = DataLoader(data_dir) if data_dir else DataLoader()
        self.mrp_engine = MRPEngine(self.loader)
        self.optimizer = SourcingOptimizer(self.loader)
        self.capacity_engine = CapacityEngine(self.loader)
        self.markdown_engine = MarkdownEngine(self.loader)
        self.financial_engine = FinancialEngine(self.loader)
        self.workflow_manager = SOPWorkflowManager(self.loader)
        self.scenario_simulator = ScenarioSimulator(self.loader)

    def run_full_pipeline(self) -> Dict[str, Any]:
        """
        Executes complete S&OP planning run and persists all 5 output tables:
        1. material_requirements.csv
        2. optimized_procurement_plan.csv
        3. production_plan.csv
        4. markdown_recommendations.csv
        5. sop_decisions.csv
        """
        print("[1/5] Running Demand Aggregation & BOM Netting...")
        mrp_df = self.mrp_engine.run_netting()

        print("[2/5] Running PuLP Sourcing & Procurement Optimization...")
        opt_df = self.optimizer.optimize_procurement(mrp_df)

        print("[3/5] Evaluating Plant Capacity Feasibility...")
        cap_df = self.capacity_engine.check_capacity_feasibility()

        print("[4/5] Evaluating In-Season Sell-Through & Markdowns...")
        mark_df = self.markdown_engine.evaluate_sell_through_and_markdowns()

        print("[5/5] Calculating Financial Rollup & Gross Margin...")
        fin_summary = self.financial_engine.calculate_financials(None, opt_df, mark_df)

        s004_comparison = self.optimizer.get_before_after_s004_comparison(opt_df)
        cycle_status = self.workflow_manager.get_cycle_status()

        print("SUCCESS: Full S&OP Pipeline executed successfully.")
        return {
            "financial_summary": fin_summary,
            "s004_tradeoff": s004_comparison,
            "cycle_status": cycle_status,
            "output_counts": {
                "material_requirements": len(mrp_df),
                "optimized_procurement_plan": len(opt_df),
                "production_plan": len(cap_df),
                "markdown_recommendations": len(mark_df),
                "sop_decisions": cycle_status["total_decisions_logged"]
            }
        }


if __name__ == "__main__":
    orchestrator = SOPOrchestrator()
    results = orchestrator.run_full_pipeline()
    print("\n--- S&OP PIPELINE EXECUTION SUMMARY ---")
    print(f"Gross Revenue:         ${results['financial_summary']['gross_revenue']:,.2f}")
    print(f"Material COGS:         ${results['financial_summary']['material_cogs']:,.2f}")
    print(f"Net Gross Margin:      ${results['financial_summary']['net_gross_margin']:,.2f} ({results['financial_summary']['gross_margin_pct']}%)")
    print(f"Output Tables Saved in: {OUTPUT_DIR}")
