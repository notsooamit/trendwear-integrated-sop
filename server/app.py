"""
TrendWear Integrated S&OP - FastAPI Backend Server
Serves all 10 S&OP modules, PuLP optimization, scenario simulation, and decision state machine.
"""

import os
import pandas as pd
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

from engine.data_loader import DataLoader, OUTPUT_DIR
from engine.mrp_engine import MRPEngine
from engine.optimizer import SourcingOptimizer
from engine.capacity_engine import CapacityEngine
from engine.markdown_engine import MarkdownEngine
from engine.financial_engine import FinancialEngine
from engine.sop_workflow import SOPWorkflowManager
from engine.scenario_simulator import ScenarioSimulator
from engine.orchestrator import SOPOrchestrator

app = FastAPI(
    title="TrendWear S&OP Enterprise Platform API",
    description="Synchronized Demand, Sourcing Optimization, Capacity Feasibility, Markdown & Financials",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engine Singletons
loader = DataLoader()
mrp_engine = MRPEngine(loader)
optimizer = SourcingOptimizer(loader)
capacity_engine = CapacityEngine(loader)
markdown_engine = MarkdownEngine(loader)
financial_engine = FinancialEngine(loader)
workflow_manager = SOPWorkflowManager(loader)
scenario_simulator = ScenarioSimulator(loader)
orchestrator = SOPOrchestrator()


# Pydantic Schemas
class ScenarioRequest(BaseModel):
    category: str = "Jackets"
    demand_pct_change: float = 50.0
    fabric_lead_time_delay_weeks: int = 1
    plant_p003_capacity_pct: float = 0.0
    supplier_s004_capacity_pct: float = -30.0


class ShiftCapacityRequest(BaseModel):
    source_plant: str = "P003"
    target_plant: str = "P004"
    period: str = "W06"
    units_to_shift: int = 1440


class DecisionRequest(BaseModel):
    cycle_id: str = "CYCLE_2026_M08"
    stage: str = "EXECUTIVE_REVIEW"
    owner_role: str = "Executive S&OP Chair"
    decision: str
    status: str = "APPROVED"
    reason: str
    financial_impact: str = "Normal"
    risk_impact: str = "Normal"
    approved_by: str


# -------------------------------------------------------------
# REST ENDPOINTS
# -------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ONLINE", "version": "1.0.0", "application": "TrendWear S&OP Engine"}


@app.get("/api/dashboard")
def get_dashboard():
    """Returns Executive Cockpit overview, KPIs, and top risks."""
    fin = financial_engine.calculate_financials()
    s004_tradeoff = optimizer.get_before_after_s004_comparison()
    cycle = workflow_manager.get_cycle_status()
    cap_df = capacity_engine.check_capacity_feasibility()
    mrp_df = mrp_engine.run_netting()
    mark_df = markdown_engine.evaluate_sell_through_and_markdowns()

    # Calculate high-level KPIs
    total_deficits = int((mrp_df["is_deficit"] == True).sum())
    bottleneck_plants = int((cap_df["capacity_status"] == "OVERLOADED").sum())
    stockout_risks = int((mark_df["action_alert"] == "STOCKOUT_VULNERABILITY_ALERT").sum())
    markdown_skus = int((mark_df["recommended_discount_pct"] > 0).sum())

    top_risks = [
        {"id": "RSK-01", "level": "HIGH", "title": "Plant P003 Capacity Overload", "detail": "108% utilization in Week 6 (+1,440 units excess)", "owner": "Production"},
        {"id": "RSK-02", "level": "HIGH", "title": "Supplier S004 Sourcing Delay", "detail": "7-week lead time with 72% OTD requires volume split", "owner": "Procurement"},
        {"id": "RSK-03", "level": "HIGH", "title": "SKU_021 Stock-Out Vulnerability", "detail": "Fast mover with only 2.1 Weeks of Stock", "owner": "Merchandising"},
        {"id": "RSK-04", "level": "MEDIUM", "title": "SKU_037 Slow Mover Working Capital Tie-up", "detail": "9,600 units (18.5 WOS) requires 35% markdown", "owner": "Merchandising"},
        {"id": "RSK-05", "level": "MEDIUM", "title": "Critical Fabric FAB_014 Lead Time", "detail": "6-week lead time necessitates immediate PO release", "owner": "Procurement"}
    ]

    return {
        "kpis": {
            "gross_revenue": fin["gross_revenue"],
            "material_cogs": fin["material_cogs"],
            "logistics_cost": fin["logistics_cost"],
            "markdown_erosion": fin["markdown_erosion"],
            "net_gross_margin": fin["net_gross_margin"],
            "gross_margin_pct": fin["gross_margin_pct"],
            "total_demand_units": fin["total_demand_units"],
            "overall_capacity_utilization": round(float(cap_df["utilization_pct"].mean()), 1),
            "material_deficits_count": total_deficits,
            "bottlenecks_count": bottleneck_plants,
            "stockout_alerts_count": stockout_risks,
            "markdown_skus_count": markdown_skus
        },
        "s004_tradeoff": s004_tradeoff,
        "cycle_status": cycle,
        "top_risks": top_risks,
        "waterfall": fin["waterfall"]
    }


@app.get("/api/demand")
def get_demand():
    """Returns rolling demand forecasts by category, region, and SKU."""
    demand_df = loader.seasonal_demand
    sku_m = loader.sku_master
    merged = demand_df.merge(sku_m[["sku_id", "category", "sku_name", "unit_retail_price"]], on="sku_id", how="left")

    # By category and period
    by_category = merged.groupby(["category", "period"])["forecasted_demand_units"].sum().reset_index()
    # By region and period
    by_region = merged.groupby(["region", "period"])["forecasted_demand_units"].sum().reset_index()
    # SKU level top items
    by_sku = merged.groupby(["sku_id", "sku_name", "category"]).agg(
        total_demand=("forecasted_demand_units", "sum"),
        unit_price=("unit_retail_price", "first")
    ).reset_index().sort_values("total_demand", ascending=False)

    return {
        "categories": by_category.to_dict("records"),
        "regions": by_region.to_dict("records"),
        "skus": by_sku.head(50).to_dict("records")
    }


@app.get("/api/materials")
def get_materials():
    """Returns BOM explosion & Time-Phased Material Requirements (MRP)."""
    mrp_df = mrp_engine.run_netting()
    # Summary by fabric
    summary = mrp_df.groupby(["fabric_id", "fabric_name", "criticality"]).agg(
        total_gross_req=("gross_requirement_meters", "sum"),
        total_net_req=("net_requirement_meters", "sum"),
        avg_inv_coverage=("inventory_coverage_pct", "mean"),
        lead_time_weeks=("lead_time_weeks", "first")
    ).reset_index().sort_values("total_net_req", ascending=False)

    return {
        "fabric_summary": summary.to_dict("records"),
        "time_phased": mrp_df.to_dict("records")
    }


@app.get("/api/procurement")
def get_procurement():
    """Returns PuLP Optimized Sourcing & Procurement Plan."""
    opt_df = optimizer.optimize_procurement()
    tradeoff = optimizer.get_before_after_s004_comparison(opt_df)
    
    # Aggregation by supplier
    by_supplier = opt_df.groupby(["supplier_id", "supplier_name", "supplier_risk_category"]).agg(
        total_allocated_meters=("recommended_order_qty", "sum"),
        total_purchase_cost=("purchase_cost", "sum"),
        mean_risk_score=("supplier_risk_score", "mean")
    ).reset_index().sort_values("total_purchase_cost", ascending=False)

    return {
        "procurement_plan": opt_df.to_dict("records"),
        "supplier_allocation_summary": by_supplier.to_dict("records"),
        "s004_tradeoff": tradeoff
    }


@app.get("/api/suppliers")
def get_suppliers():
    """Returns Supplier Master Risk profiles and matrix."""
    sup = optimizer.compute_supplier_risk_scores()
    return {"suppliers": sup.to_dict("records")}


@app.get("/api/capacity")
def get_capacity():
    """Returns Plant Production Capacity Loading & Heatmap."""
    cap_df = capacity_engine.check_capacity_feasibility()
    
    # Grouped by plant
    by_plant = cap_df.groupby(["plant_id", "plant_name", "region"]).agg(
        mean_utilization=("utilization_pct", "mean"),
        max_utilization=("utilization_pct", "max"),
        overload_weeks=("capacity_status", lambda s: int((s == "OVERLOADED").sum()))
    ).reset_index()

    return {
        "plant_capacity": cap_df.to_dict("records"),
        "plant_summary": by_plant.to_dict("records")
    }


@app.post("/api/capacity/shift")
def shift_capacity(req: ShiftCapacityRequest):
    """Reallocates units from overloaded plant to flex plant."""
    try:
        res = capacity_engine.shift_production(
            source_plant=req.source_plant,
            target_plant=req.target_plant,
            period=req.period,
            units_to_shift=req.units_to_shift
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/inventory")
def get_inventory():
    """Returns DC Inventory balances, safety buffers, and logistics lanes."""
    inv_df = loader.current_inventory
    log_df = loader.logistics
    sku_m = loader.sku_master

    merged_inv = inv_df.merge(sku_m[["sku_id", "category", "sku_name", "unit_retail_price"]], on="sku_id", how="left")

    by_dc = merged_inv.groupby("location_id").agg(
        total_available=("available_stock_units", "sum"),
        total_reserved=("reserved_stock_units", "sum"),
        total_safety=("safety_stock_threshold", "sum"),
        avg_age_days=("inventory_age_days", "mean")
    ).reset_index()

    return {
        "dc_summary": by_dc.to_dict("records"),
        "inventory_records": merged_inv.to_dict("records"),
        "logistics_lanes": log_df.to_dict("records")
    }


@app.get("/api/sell-through")
@app.get("/api/markdowns")
def get_sell_through_and_markdowns():
    """Returns In-Season Sell-Through, Mover Classifications, Stock-Out Alerts & Markdowns."""
    mark_df = markdown_engine.evaluate_sell_through_and_markdowns()
    
    # Aggregation by mover class
    by_class = mark_df.groupby("mover_class").agg(
        sku_count=("sku_id", "count"),
        total_on_hand=("current_on_hand_units", "sum"),
        total_value_at_risk=("inventory_value_at_risk", "sum"),
        mean_wos=("weeks_of_stock", "mean")
    ).reset_index()

    # High priority alerts
    critical_alerts = mark_df[mark_df["action_alert"] != "HEALTHY_VELOCITY"].sort_values("weeks_of_stock", ascending=False)

    return {
        "sku_recommendations": mark_df.to_dict("records"),
        "class_summary": by_class.to_dict("records"),
        "critical_alerts": critical_alerts.to_dict("records")
    }


@app.get("/api/financials")
def get_financials():
    """Returns Financial Waterfall and Gross Margin Breakdown."""
    fin = financial_engine.calculate_financials()
    return fin


@app.post("/api/scenario/run")
def run_scenario(req: ScenarioRequest):
    """Simulates real-time What-If scenario against baseline."""
    res = scenario_simulator.run_scenario(
        category=req.category,
        demand_pct_change=req.demand_pct_change,
        fabric_lead_time_delay_weeks=req.fabric_lead_time_delay_weeks,
        plant_p003_capacity_pct=req.plant_p003_capacity_pct,
        supplier_s004_capacity_pct=req.supplier_s004_capacity_pct
    )
    return res


@app.get("/api/sop/cycle")
def get_sop_cycle():
    """Returns S&OP 5-Stage Monthly Workflow Status and Decision Log."""
    status = workflow_manager.get_cycle_status()
    decisions = workflow_manager.get_decisions()
    return {
        "status": status,
        "decisions": decisions.to_dict("records")
    }


@app.post("/api/sop/decide")
def record_sop_decision(req: DecisionRequest):
    """Records an auditable S&OP decision."""
    res = workflow_manager.record_decision(
        cycle_id=req.cycle_id,
        stage=req.stage,
        owner_role=req.owner_role,
        decision=req.decision,
        status=req.status,
        reason=req.reason,
        financial_impact=req.financial_impact,
        risk_impact=req.risk_impact,
        approved_by=req.approved_by
    )
    return res


@app.post("/api/pipeline/run")
def trigger_pipeline():
    """Re-runs the entire pipeline and refreshes all outputs."""
    res = orchestrator.run_full_pipeline()
    return res

# Static files for web app (served from web/dist or web/public)
WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web")
if os.path.exists(WEB_DIR):
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="static")
