"""
TrendWear S&OP 5-Stage Monthly Workflow & Decision State Machine
Tracks stages: Demand Review -> Supply Review -> Financial Review -> Executive S&OP -> Execution.
Maintains auditable decisions in sop_decisions.csv.
"""

import os
import time
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from .data_loader import DataLoader, OUTPUT_DIR

STAGES = [
    "DEMAND_REVIEW",
    "SUPPLY_REVIEW",
    "FINANCIAL_REVIEW",
    "EXECUTIVE_REVIEW",
    "EXECUTION",
    "MONITORING"
]

STAGE_ROLES = {
    "DEMAND_REVIEW": "Merchandising Lead",
    "SUPPLY_REVIEW": "Supply Chain / Procurement Lead",
    "FINANCIAL_REVIEW": "Finance Director",
    "EXECUTIVE_REVIEW": "VP of Operations / Executive S&OP",
    "EXECUTION": "Operations Team",
    "MONITORING": "Cross-Functional Leads"
}


class SOPWorkflowManager:
    def __init__(self, loader: DataLoader):
        self.loader = loader
        self.decisions_file = os.path.join(OUTPUT_DIR, "sop_decisions.csv")
        self._init_decisions_table()

    def _init_decisions_table(self):
        if not os.path.exists(self.decisions_file):
            initial_decisions = [
                {
                    "sop_cycle_id": "CYCLE_2026_M08",
                    "stage": "DEMAND_REVIEW",
                    "owner_role": "Merchandising Lead",
                    "decision": "Approve Baseline Demand Forecast with +50% Week 6 Jacket Uplift",
                    "status": "APPROVED",
                    "reason": "Aligned with upcoming FW26 marketing launch campaign across NA and EU.",
                    "financial_impact": "+$185,000 Revenue",
                    "risk_impact": "Requires early fabric commitment for FAB_014",
                    "approved_by": "Sarah Chen (Merchandising VP)",
                    "timestamp": "2026-08-10 14:30:00"
                },
                {
                    "sop_cycle_id": "CYCLE_2026_M08",
                    "stage": "SUPPLY_REVIEW",
                    "owner_role": "Procurement Lead",
                    "decision": "Approve Multi-Sourcing Optimization & Reduce S004 Allocation to 35%",
                    "status": "APPROVED",
                    "reason": "Mitigates high delay risk of supplier S004 (72% OTD) by shifting volume to S001 and S002.",
                    "financial_impact": "+2.1% Material Cost Delta",
                    "risk_impact": "-48% Late Delivery Risk",
                    "approved_by": "Marcus Vance (Head of Procurement)",
                    "timestamp": "2026-08-12 11:15:00"
                },
                {
                    "sop_cycle_id": "CYCLE_2026_M08",
                    "stage": "SUPPLY_REVIEW",
                    "owner_role": "Production Lead",
                    "decision": "Shift 1,440 units from Plant P003 to Plant P004 in Week 6",
                    "status": "APPROVED",
                    "reason": "Resolves 108% capacity overload at P003 and prevents bottlenecking.",
                    "financial_impact": "$1,200 Freight Adjustment",
                    "risk_impact": "Eliminates Plant Bottleneck (P003 -> 100%, P004 -> 85%)",
                    "approved_by": "David Ramos (Plant Operations)",
                    "timestamp": "2026-08-12 16:45:00"
                },
                {
                    "sop_cycle_id": "CYCLE_2026_M08",
                    "stage": "FINANCIAL_REVIEW",
                    "owner_role": "Finance Director",
                    "decision": "Approve Target Gross Margin Plan of 31.4%",
                    "status": "APPROVED",
                    "reason": "Margin trade-off for supply resilience approved within authorized tolerance (+/- 1.5%).",
                    "financial_impact": "$1.42M Gross Margin Projected",
                    "risk_impact": "Financial exposure balanced with $85k markdown reserves",
                    "approved_by": "Elena Rostova (CFO)",
                    "timestamp": "2026-08-13 09:30:00"
                },
                {
                    "sop_cycle_id": "CYCLE_2026_M08",
                    "stage": "EXECUTIVE_REVIEW",
                    "owner_role": "Executive S&OP Chair",
                    "decision": "Lock Integrated S&OP Plan for Cycle 2026_M08",
                    "status": "LOCKED",
                    "reason": "All cross-functional reviews completed; production orders released to ERP.",
                    "financial_impact": "Fully Reconciled Plan",
                    "risk_impact": "Executive Sign-Off",
                    "approved_by": "Robert Sterling (COO)",
                    "timestamp": "2026-08-14 17:00:00"
                }
            ]
            df = pd.DataFrame(initial_decisions)
            df.to_csv(self.decisions_file, index=False)

    def get_decisions(self) -> pd.DataFrame:
        return pd.read_csv(self.decisions_file)

    def record_decision(self, cycle_id: str, stage: str, owner_role: str, decision: str, status: str, reason: str, financial_impact: str, risk_impact: str, approved_by: str) -> Dict[str, Any]:
        df = self.get_decisions()
        new_row = {
            "sop_cycle_id": cycle_id,
            "stage": stage,
            "owner_role": owner_role,
            "decision": decision,
            "status": status,
            "reason": reason,
            "financial_impact": financial_impact,
            "risk_impact": risk_impact,
            "approved_by": approved_by,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(self.decisions_file, index=False)
        return new_row

    def get_cycle_status(self) -> Dict[str, Any]:
        df = self.get_decisions()
        latest_status = df.iloc[-1]["status"] if len(df) > 0 else "DRAFT"
        current_stage = df.iloc[-1]["stage"] if len(df) > 0 else "DEMAND_REVIEW"
        return {
            "current_cycle_id": "CYCLE_2026_M08",
            "current_stage": current_stage,
            "stage_owner": STAGE_ROLES.get(current_stage, "Executive"),
            "status": latest_status,
            "stages_flow": STAGES,
            "total_decisions_logged": len(df),
            "is_plan_locked": latest_status == "LOCKED"
        }
