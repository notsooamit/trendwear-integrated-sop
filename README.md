# TrendWear™ Integrated S&OP Enterprise Platform

> **Deterministic, Multi-Echelon Sales & Operations Planning Platform for Fast-Fashion Retail**  
> Synchronizing commercial demand forecasting, multi-supplier MILP sourcing, plant capacity balancing, in-season markdowns, and executive financial governance.

---

## 1. Overview

**TrendWear** launches new seasonal apparel lines every **6 weeks**, operating under rigid **4 to 6-week fabric procurement lead times** from global textile mills. Disconnected departmental spreadsheets historically led to forecast mismatches (overproduction of slow movers and stock-outs of fast sellers), plant capacity overloads, and margin erosion.

This platform provides an end-to-end, automated, and mathematically optimized S&OP system designed for cross-functional collaboration across **Merchandising, Procurement, Production, Logistics, and Executive Leadership**.

---

## 2. Core Capabilities & Architecture

1. **Commercial Demand Forecasting & Merchandising Overrides**:
   - Rolling 6-week and 12-week time-phased demand projections across 50 SKUs and 4 global regions.
   - Interactive trend uplifts with automatic downstream MRP explosion and financial margin recalculation.
2. **Multi-Echelon BOM Netting (MRP Engine)**:
   - Automated conversion from finished garment demand to 30 raw fabric requirements with cutting scrap adjustments.
   - Inventory buffer netting against on-hand DC stock and safety stock thresholds.
3. **Multi-Supplier Sourcing Optimization (PuLP MILP Solver)**:
   - Mixed-Integer Linear Programming allocating volume across 8 global suppliers.
   - Strict enforcement of Minimum Order Quantities (MOQ), supplier risk profiles, and backward PO scheduling.
   - Live client-side MOQ validation warning badges and 1-click PO export (CSV / Copy).
4. **Plant Capacity Scheduling & Bottleneck Rebalancing**:
   - Factory loading evaluation across 5 global manufacturing hubs ($P001 \dots P005$).
   - Dynamic bottleneck rebalancing (e.g. shifting 1,440 units from overloaded $P003$ to $P004$ flex line) with persistent disk synchronization.
5. **In-Season Sell-Through & Markdown Elasticity Engine**:
   - Velocity tracking classifying items into Fast, Normal, and Slow movers based on empirical percentiles ($P_{75} / P_{25}$) and Weeks of Stock (WOS).
   - Dynamic promotional markdown depth recommendations ($15\%$ to $50\%$) maximizing working capital recovery.
6. **Executive Financial P&L Waterfall**:
   - Direct reconciliation of Gross Revenue, Material COGS, Logistics Freight, and Markdown Loss.
   - Real-time gross margin hurdle verification ($\ge 30.0\%$ target vs. $33.0\%$ baseline).
7. **What-If Strategy Simulator & 5-Stage Governance Board**:
   - Sub-second scenario stress-testing for demand surges ($+50\%$), lead-time disruptions ($+2\text{ wks}$), and supplier capacity losses.
   - Tamper-evident audit logging for the monthly 5-stage consensus cadence ($W1 \rightarrow W2 \rightarrow W3 \rightarrow W4 \rightarrow \text{Lock}$).

---

## 3. Repository Structure

```text
SOP/
├── .gitignore                          # Standard git ignore patterns
├── README.md                           # Project documentation & overview
├── Problem Statement.txt               # Fast-fashion business requirements
├── data/                               # Relational CSV Datasets (20 Tables, 7,557 Tuples)
│   ├── master/                         # Master catalogs (SKU, Fabric, Supplier, Plant, BOM, Pricing)
│   ├── demand/                         # Seasonal commercial demand forecasts
│   ├── production/                     # Weekly plant production capacity
│   ├── inventory/                      # DC warehouse stock & safety buffers
│   ├── sales/                          # Historical sell-through & promotional markdown elasticity
│   ├── logistics/                      # DC-to-store transportation lanes & SLAs
│   └── outputs/                        # Optimized procurement plans, decisions & production schedules
├── docs/                               # Formal Technical & Business Documentation
│   ├── DATASET_SPECIFICATION.md        # Relational schema, ERD, and data dictionary
│   ├── BUSINESS_FLOW_SPECIFICATION.md  # 8 core flows, sequence diagrams, and mathematical models
│   ├── ARCHITECTURE_SPECIFICATION.md   # Multi-tier architecture, engine designs, and REST API contracts
│   └── GAP_ANALYSIS_AND_IMPROVEMENTS.md# In-scope audit log & resolution backlog
├── engine/                             # Core Computational & Optimization Engines (Python)
│   ├── data_loader.py                  # In-memory relational join & cache manager
│   ├── mrp_engine.py                   # Multi-echelon BOM explosion & netting
│   ├── optimizer.py                    # PuLP MILP multi-supplier sourcing solver
│   ├── capacity_engine.py              # Plant capacity evaluation & line rebalancer
│   ├── markdown_engine.py              # In-season velocity & price elasticity model
│   ├── financial_engine.py             # P&L waterfall & gross margin rollup
│   ├── sop_workflow.py                 # 5-stage monthly S&OP consensus state machine
│   ├── scenario_simulator.py           # Sub-second What-If strategy solver
│   └── orchestrator.py                 # End-to-end pipeline orchestrator
├── scripts/                            # Verification & Data Generation Scripts
│   ├── generate_synthetic_data.py      # Relational synthetic data generator
│   └── test_system_health.py           # 14-point automated subsystem audit script
├── server/                             # Multi-Threaded HTTP & REST Server
│   └── http_server.py                  # Thread-safe REST API server (Port 8000)
└── web/                                # Role-Segmented Responsive Web Application
    ├── index.html                      # Semantic workspace layout
    ├── style.css                       # Premium dark-mode design system
    └── app.js                          # Reactive ES6 client controller
```

---

## 4. Quick Start & Execution

### Prerequisites
- Python 3.10+
- Dependencies: `pandas`, `pulp`, `numpy`

```bash
pip install pandas pulp numpy
```

### Launching the Application
```bash
python -m server.http_server
```
Open your browser and navigate to:
```text
http://localhost:8000
```

### Role-Based Access Credentials
Default password for all roles: `password`

| Role Username | Persona | Default Viewport |
|---|---|---|
| `executive` | Elena Rostova (Executive S&OP Chair) | Executive Cockpit & Financial Waterfall |
| `planner` | Sarah Chen (Demand & Merchandising Lead) | Demand Planning & Forecasting |
| `procurement` | Marcus Vance (Procurement & Sourcing Lead) | Sourcing & Multi-Supplier Optimization |
| `production` | David Miller (Plant & Production Lead) | Plant Capacity & Bottleneck Shifter |
| `logistics` | Carlos Gomez (Logistics & DC Network Lead) | Inventory & DC Logistics Lanes |

---

## 5. System Health Verification

Execute the automated 14-point health audit:
```bash
python scripts/test_system_health.py
```

---

## 6. Formal Documentation Suite

For detailed technical references, refer to the documentation in [`docs/`](docs/):
- [Dataset Specification & Data Dictionary](docs/DATASET_SPECIFICATION.md)
- [Core Business Flows & Mathematical Logic](docs/BUSINESS_FLOW_SPECIFICATION.md)
- [Technical Architecture & API Specifications](docs/ARCHITECTURE_SPECIFICATION.md)
- [Gap Analysis & Verified Improvements](docs/GAP_ANALYSIS_AND_IMPROVEMENTS.md)
