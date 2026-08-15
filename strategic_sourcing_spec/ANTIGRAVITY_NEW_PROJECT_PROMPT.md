# MASTER ANTIGRAVITY BLUEPRINT: STRATEGIC SOURCING & MULTI-SUPPLIER ALLOCATION ENTERPRISE PLATFORM

> **Copy and paste the entire prompt below into a new Antigravity chat session inside a new project folder (e.g. `StrategicSourcing/`) to build the complete industrial manufacturing procurement platform from scratch.**

---

````markdown
# TASK: BUILD COMPLETE STRATEGIC SOURCING & MULTI-SUPPLIER ALLOCATION ENTERPRISE PLATFORM

## 1. PROJECT OVERVIEW & CORE OBJECTIVES

Design and build an enterprise-grade, deterministic **Strategic Sourcing & Multi-Supplier Allocation Platform** for an industrial manufacturing enterprise. The system optimizes direct raw material procurement across multiple manufacturing assembly plants while rigorously balancing landed purchase costs, supplier delivery reliability, quality defect ratings, capacity limits, and contractual diversification commitments.

### Expected Core Outcomes:
1. **Multi-Objective Sourcing Optimization (PuLP MILP)**: Efficiently allocate material procurement quantities across 12 approved global suppliers for 40 direct industrial raw materials supplying 5 manufacturing assembly plants over a 12-week planning horizon.
2. **Strict Supplier-Material Compatibility Enforcement**: Enforce the physical manufacturing capability matrix—*not all suppliers can supply all material categories*. Only certified, approved supplier-material pairs ($s \in \text{Certified}(m)$) may receive allocations.
3. **Landed Cost Minimization with Quality & Risk Bounds**: Minimize total landed cost (unit price + inter-plant freight + order setup overhead) while enforcing quality defect ceilings ($\text{PPM} \le 250$), delivery reliability bounds ($\text{OTD} \ge 90\%$), and supplier maximum weekly capacity limits.
4. **Contractual Minimum & Maximum Allocation Share Bands**: Enforce anti-concentration diversification bands (e.g., minimum 15% secondary sourcing commitment, maximum 60% primary supplier cap) to prevent single-source vulnerability.
5. **Pre-PO Predictive Delivery Delay Probability Engine**: Predict potential transit and manufacturing delivery delays prior to purchase order dispatch using supplier historical performance variance, current factory backlog loading, and logistics risk scores.
6. **Interactive What-If Disruption Simulator**: Provide sub-second stress-testing for supplier shutdowns (0% capacity), plant production surges (+45%), lead-time maritime transit delays (+3 weeks), and quality threshold tightening.
7. **5-Stage Sourcing Governance & Decision Ledger**: Track cross-functional procurement approvals (Demand Aggregation -> Supplier Scorecard -> MILP Optimization -> Predictive Delay Review -> Executive Award) with tamper-evident audit logging.

---

## 2. TECHNOLOGY STACK & ARCHITECTURAL GUIDELINES

- **Backend Runtime**: Python 3.10+ Standard Library (`http.server`, `socketserver`, `threading`, `json`, `urllib`). Zero heavy backend framework dependencies. Run on port 8000 (binding to dynamic `$PORT` environment variable for cloud deployment).
- **Optimization Solver**: PuLP Mixed-Integer Linear Programming (MILP) using the bundled Coin-OR CBC solver.
- **Data Layer**: Pandas vectorized in-memory relational DataFrames with atomic CSV persistence to disk.
- **Frontend Architecture**: Pure Vanilla HTML5, Vanilla CSS3 (Custom Dark-Mode Glassmorphic Design System), and Reactive Vanilla ES6+ JavaScript. Zero build steps, zero npm/webpack dependencies.
- **Visualization & Icons**: Lucide Icons & Chart.js loaded via CDN.

---

## 3. RELATIONAL DATASET SCHEMA (13 RELATIONAL CSV TABLES)

Create a `scripts/generate_synthetic_data.py` script that deterministically populates the following 13 relational CSV datasets in `data/`:

### 3.1 Master Data Layer (`data/master/`)
1. `material_master.csv`: `material_id` (MAT_001 to MAT_040), `material_name`, `category` (*Structural Steel, Aluminum Alloys, Polymers & Resins, Electronic Subassemblies, Precision Bearings, Hydraulics, High-Tensile Fasteners, Industrial Composites*), `unit_of_measure` (*kg, meters, units*), `standard_cost_usd` ($5.00 to $450.00), `criticality` (*HIGH, MEDIUM, LOW*). (40 rows)
2. `supplier_master.csv`: `supplier_id` (SUP_001 to SUP_012), `supplier_name`, `country` (*USA, Germany, Japan, South Korea, Mexico, Vietnam, India, Taiwan*), `tier` (*Tier-1, Tier-2*), `base_financial_risk_score` (1.0 to 5.0), `iso_certified` (*TRUE/FALSE*). (12 rows)
3. `plant_master.csv`: `plant_id` (PLANT_01 to PLANT_05), `plant_name`, `location` (*Detroit, Munich, Monterrey, Tokyo, Chennai*), `weekly_assembly_capacity_units` (8,000 to 25,000 units). (5 rows)
4. `bom_direct_materials.csv`: `sku_id` (SKU_001 to SKU_030), `material_id`, `usage_qty_per_unit`, `scrap_allowance_pct` (0.02 to 0.08). (120 rows)

### 3.2 Sourcing Terms & Performance Layer (`data/suppliers/`)
5. `supplier_material_pricing.csv`: `supplier_id`, `material_id`, `unit_price_usd`, `moq_units`, `standard_lead_time_weeks` (1 to 8 wks). (120 rows representing certified supplier-material pairs—each supplier is certified for 8–12 specific materials).
6. `supplier_capacity_limits.csv`: `supplier_id`, `material_id`, `period_week` (W01 to W12), `max_weekly_capacity_units`. (1,440 rows)
7. `supplier_scorecards.csv`: `supplier_id`, `historical_otd_pct` (78.0% to 98.5%), `defect_ppm` (45 to 850 PPM), `quality_audit_score` (1 to 100), `lead_time_variance_days` (0.5 to 6.2 days), `reliability_rating` (*EXCELLENT, GOOD, MARGINAL, HIGH_RISK*). (12 rows)
8. `contract_commitments.csv`: `supplier_id`, `material_id`, `min_guaranteed_share_pct` (0.10 to 0.20), `max_allocation_cap_pct` (0.50 to 0.70). (120 rows)

### 3.3 Demand & Logistics Layer (`data/demand/` & `data/logistics/`)
9. `plant_material_demand.csv`: `material_id`, `plant_id`, `period_week` (W01 to W12), `forecasted_demand_units`. (2,400 rows)
10. `current_inventory.csv`: `material_id`, `plant_id`, `available_on_hand_units`, `safety_stock_threshold_units`. (200 rows)
11. `freight_lane_matrix.csv`: `supplier_id`, `plant_id`, `transit_time_days` (1 to 24 days), `freight_cost_per_unit_usd` ($0.45 to $12.50), `lane_reliability_pct` (88% to 99%). (60 rows)

### 3.4 Optimization Output Layer (`data/outputs/`)
12. `optimized_sourcing_plan.csv`: `material_id`, `supplier_id`, `plant_id`, `period_week`, `allocated_units`, `landed_cost_usd`, `po_release_week`, `expected_delivery_week`, `moq_compliance_status`.
13. `sourcing_decisions.csv`: `cycle_id`, `stage`, `owner_role`, `decision`, `financial_impact`, `risk_impact`, `status`, `approved_by`, `timestamp`.

---

## 4. COMPUTATIONAL ENGINES ARCHITECTURE (`engine/`)

Implement the following modular Python classes in `engine/`:

1. `data_loader.py` (`DataLoader`): Loads and caches relational CSV files, provides vectorized helper properties, and performs inner-join validation on certified supplier-material pairs.
2. `mrp_engine.py` (`MRPEngine`): Explodes BOM demand across 30 finished SKUs and 5 assembly plants, calculating time-phased gross requirements and net material deficits:
   $$\text{NetReq}_{m,p,t} = \max(0, \text{GrossReq}_{m,p,t} + \text{SafetyStock}_{m,p} - \text{OnHand}_{m,p} - \text{Receipts}_{m,p,t})$$
3. `optimizer.py` (`SourcingOptimizer`): Formulates and executes the Mixed-Integer Linear Program using `pulp.LpProblem`:
   - **Decision Variables**: $x_{s,m,p,t} \ge 0$ (allocated material volume), $y_{s,m,t} \in \{0, 1\}$ (binary supplier activation flag).
   - **Objective Function**:
     $$\min \sum_{s,m,p,t} \left[ (\text{UnitPrice}_{s,m} + \text{Freight}_{s,p}) \cdot x_{s,m,p,t} + \lambda_{\text{risk}} \cdot R_s \cdot x_{s,m,p,t} \right] + \sum_{s,m,t} \text{SetupCost} \cdot y_{s,m,t}$$
   - **Constraints**:
     - Demand Satisfaction: $\sum_{s \in \text{Certified}(m)} x_{s,m,p,t} \ge \text{NetReq}_{m,p,t}$
     - Material Compatibility: $x_{s,m,p,t} \le M \cdot \mathcal{C}_{s,m}$
     - Supplier Capacity Bounds: $\sum_p x_{s,m,p,t} \le \text{MaxCap}_{s,m,t} \cdot y_{s,m,t}$
     - Contract MOQ Limits: $\sum_p x_{s,m,p,t} \ge \text{MOQ}_{s,m} \cdot y_{s,m,t}$
     - Contract Share Bands: $\text{MinShare}_{s,m} \cdot \sum_i x_{i,m,p,t} \le x_{s,m,p,t} \le \text{MaxShare}_{s,m} \cdot \sum_i x_{i,m,p,t}$
     - Quality Defect Ceiling: Weighted average $\text{PPM} \le 250$.
4. `supplier_scorecard_engine.py` (`ScorecardEngine`): Computes composite supplier reliability indices $R_s$ balancing OTD %, quality defect PPM, lead-time variance, and financial/geopolitical risk.
5. `predictive_delay_engine.py` (`PredictiveDelayEngine`): Evaluates pre-PO delivery delay probabilities using logistic probability modeling:
   $$P(\text{Delay} > 3\text{d}) = \frac{1}{1 + \exp(-(\beta_0 + \beta_1 \cdot \text{CapacityUtil}_s + \beta_2 \cdot \text{Variance}_s + \beta_3 \cdot \text{OrderRatio} + \beta_4 \cdot \text{GeoRisk}_s))}$$
6. `spend_analytics_engine.py` (`SpendEngine`): Calculates total procurement spend, landed cost waterfalls, contract savings realized, and spend concentration HHI index.
7. `scenario_simulator.py` (`ScenarioSimulator`): Executes sub-second parametric What-If stress-tests (supplier capacity disruptions, demand surges, lead-time delays, quality standard tightening).
8. `sourcing_workflow.py` (`SourcingWorkflowManager`): 5-stage monthly sourcing governance state machine logging immutable decision records to `sourcing_decisions.csv`.
9. `orchestrator.py` (`SourcingOrchestrator`): Executes complete pipeline recalculation and reconciliation in a single coordinated run.

---

## 5. THREAD-SAFE HTTP REST API GATEWAY (`server/http_server.py`)

Run a `ThreadedHTTPServer` on port 8000 with `state_lock = threading.Lock()`. Automatically bind to dynamic `PORT` environment variable and include `Cache-Control: no-store` headers.

### REST Endpoints:
- `GET /api/health` -> System health and subsystem operational status.
- `GET /api/dashboard` -> Executive Sourcing KPIs (Total Spend, Mean OTD %, Defect PPM, Risk Index, Savings).
- `GET /api/demand` -> Plant material demand forecasts across categories.
- `GET /api/scorecards` -> Supplier OTD, quality PPM, capability matrices, and risk ratings.
- `GET /api/procurement/plan` -> PuLP-optimized purchase order allocation matrix.
- `GET /api/delays/predictive` -> Pre-PO predictive delivery delay risk alerts.
- `GET /api/spend/analytics` -> Landed cost breakdown, spend waterfall, and supplier concentration HHI.
- `GET /api/sourcing/cycle` -> 5-Stage Sourcing Governance state machine and decision ledger.
- `GET /api/activity/feed` -> Real-time collaborative procurement event stream.
- `POST /api/demand/override` -> Adjust material demand and cascade downstream solver calculations.
- `POST /api/scenario/run` -> Execute real-time What-If disruption simulations.
- `POST /api/sourcing/decide` -> Record and sign off executive sourcing decisions.
- `POST /api/pipeline/run` -> Re-optimize complete sourcing schedule.

---

## 6. FRONTEND WORKSPACE & UI/UX REQUIREMENTS (`web/`)

Implement a dark-mode glassmorphic enterprise web interface in `web/index.html`, `web/style.css`, and `web/app.js`:

1. **Role-Based Authentication & Segmentation**:
   - Persona Profiles (password `password` for all):
     - `executive` -> Robert Sterling (Chief Procurement Officer) -> Executive Sourcing Cockpit & Spend Waterfall.
     - `sourcing_lead` -> Marcus Vance (Strategic Sourcing Category Lead) -> Sourcing Allocations & Vendor Sliders.
     - `plant_buyer` -> David Miller (Plant Materials Buyer) -> Plant Demand Netting & PO Release.
     - `quality_lead` -> Dr. Aris Thorne (Supplier Quality Assurance) -> Supplier Scorecards & PPM Audits.
   - Dynamic sidebar navigation filtering based on authenticated role.
2. **Interactive Sourcing Tuning Sliders & Live MOQ Validation**:
   - Material selector dynamically populating certified qualified suppliers.
   - Interactive vendor share sliders calculating allocated volume in real-time.
   - Visual alert badges: `⚠️ Sub-MOQ Violation: XXX units < MOQ: YYY units` if volume drops below contract minimums.
   - Live summary banner displaying Net Required, Lead Time, and Allocated Share.
3. **Universal 1-Click Purchase Order Release Modal**:
   - Displays authorized vendor, material, quantity, landed price, and OTD compliance.
   - Actions: **"Download PO (CSV)"**, **"Copy Summary"**, and **"Confirm & Release PO to EDI"**.
4. **Pre-PO Predictive Delivery Delay Radar**:
   - Visual risk indicators (Green: Low Risk <15%, Amber: Moderate 15-35%, Red: High Delay Risk >35%).
   - One-click split-sourcing contingency rebalancing button.
5. **Interactive What-If Strategy Simulator**:
   - Sliders for Supplier Capacity Loss (-100% to 0%), Demand Surge (0% to +100%), and Lead Time Delay (+0 to +4 wks).
   - 1-Click **"↺ Reset to Baseline"** action.
6. **Live Activity Stream Drawer**:
   - Slide-out collaborative stream logging procurement decisions, overrides, and solver executions.

---

## 7. AUTOMATED VERIFICATION AUDIT (`scripts/test_system_health.py`)

Provide an automated test script verifying all 14 REST endpoints, PuLP optimization execution, mathematical consistency, thread-safety, and UI zero-cache headers with 100% pass rate.

---

## 8. DEPLOYMENT CONFIGURATION

Include:
- `requirements.txt`: `pandas`, `pulp`, `numpy`, `fastapi`, `uvicorn`.
- `Procfile`: `web: python -m server.http_server`.
- `Dockerfile`: Debian-slim container with pre-installed `coinor-cbc` linear solver package.
- Dynamic `window.location.origin` API URL detection in `web/app.js`.

---

## EXECUTION DIRECTIVE:
Build this entire system in a clean, professional manner without generic slop, with complete mathematical formulations, comprehensive docstrings, full relational datasets, and zero placeholder code.
````
