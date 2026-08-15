# TrendWear Integrated S&OP Enterprise Suite
## Document 2: Core Business Flows and Decision Framework

---

### 1. Executive Process Summary

The TrendWear Integrated Sales and Operations Planning (S&OP) framework establishes a deterministic, multi-echelon business process that connects commercial demand forecasts with physical supply execution and executive financial governance.

The platform executes eight core operational flows:
1. **Commercial Demand Forecasting & Merchandising Overrides**
2. **Multi-Echelon Bill of Materials (BOM) Explosion & MRP Netting**
3. **Risk-Aware Mixed-Integer Linear Programming (MILP) Sourcing Optimization**
4. **Plant Capacity Scheduling, Bottleneck Detection & Dynamic Line Balancing**
5. **In-Season Sell-Through Velocity Monitoring & Dynamic Markdown Elasticity**
6. **DC-to-Store Logistics, Transportation Lanes & Fulfillment SLAs**
7. **Consolidated Financial Waterfall Reconciliation (P&L Hurdle Verification)**
8. **5-Stage Monthly S&OP Consensus Cadence & Governance Audit Ledger**

---

### 2. End-to-End S&OP Operational Flowchart

```mermaid
flowchart TD
    subgraph STAGE_1 [1. Demand & Merchandising Review]
        D1[Unconstrained Sales Forecast: 50 SKUs] --> D2[Merchandising Intelligence & Trend Overrides]
        D2 --> D3[Consensus Unconstrained Demand Plan]
    end

    subgraph STAGE_2 [2. Supply & Feasibility Review]
        D3 --> S1[BOM Explosion & Material Netting MRP]
        S1 --> S2{Fabric Deficit Identified?}
        S2 -- Yes --> S3[MILP Sourcing Optimization Engine: MOQs, 4-6 Wk Lead Times, Risk Scores]
        S3 --> S4[Automated Purchase Order Schedule POs]
        S2 -- No --> S5[Existing Mill Allocations Sufficient]
        
        D3 --> P1[Plant Capacity Analysis: 5 Global Hubs]
        P1 --> P2{Plant Overload Detected?}
        P2 -- Yes --> P3[Dynamic Line Balancing: Inter-Plant Production Shift]
        P2 -- No --> P4[Feasible Assembly Schedule Locked]
    end

    subgraph STAGE_3 [3. In-Season Execution & Logistics]
        P4 --> L1[Finished Goods Inbound to 4 Regional DCs]
        L1 --> L2[Store Replenishment Dispatch: 60 Retail Lanes]
        L2 --> M1[POS Sell-Through Monitoring: Weeks 1-6]
        M1 --> M2{Velocity Classification}
        M2 -- Fast Mover: WOS < 4.0 --> M3[Stockout Alert & Logistics Priority]
        M2 -- Normal Mover: WOS 4.0-8.0 --> M4[Standard Replenishment]
        M2 -- Slow Mover: WOS > 8.0 --> M5[Dynamic Markdown Clearance Simulation: 15-50% Discount]
    end

    subgraph STAGE_4 [4. Financial Reconciliation]
        S4 & P4 & L2 & M5 --> F1[Consolidated Financial Waterfall Engine]
        F1 --> F2[Gross Revenue Calculation]
        F1 --> F3[Material COGS Deduction]
        F1 --> F4[Logistics Freight Cost Deduction]
        F1 --> F5[Markdown Price Erosion Deduction]
        F2 & F3 & F4 & F5 --> F6[Consensus Net Gross Margin Hurdle Check: >= 30%]
    end

    subgraph STAGE_5 [5. Executive Review & Governance Lock]
        F6 --> E1[Executive Cockpit & What-If Strategy Simulator]
        E1 --> E2[Cross-Functional Sign-Off & Audit Logging]
        E2 --> E3[Formal S&OP Plan Committed to ERP/MES/WMS]
    end
```

---

### 3. Detailed Business Flow Specifications

#### Flow 1: Commercial Demand Forecasting & Merchandising Overrides

```mermaid
sequenceDiagram
    autonumber
    actor Planner as Demand & Merchandising Lead
    participant DemandEngine as Demand Forecasting Module
    participant DB as Seasonal Demand Repository
    actor Exec as Executive S&OP Chair

    Planner->>DemandEngine: Query unconstrained statistical forecast (W01-W12 across 50 SKUs)
    DemandEngine->>DB: Fetch baseline seasonal trends and regional splits
    DB-->>DemandEngine: Return 3,000 demand records
    DemandEngine-->>Planner: Render aggregated category and regional demand profiles
    Planner->>DemandEngine: Apply market intelligence override (e.g., +50% Jackets holiday surge)
    DemandEngine->>DemandEngine: Recalculate SKU-level distributions and revenue potential
    DemandEngine-->>Exec: Broadcast updated demand plan to Executive Cockpit
```

* **Business Objective**: Establish the unconstrained commercial target while accommodating merchandising trend adjustments.
* **Input Parameters**:
  - Statistical time-series forecast per SKU, region, and week ($50\text{ SKUs} \times 5\text{ Regions} \times 12\text{ Weeks}$).
  - Full-price MSRP per SKU ($29.50 to $149.00).
* **Decision Rules**:
  - Overrides can be executed at the style/SKU level or broad category level.
  - When an override is submitted, the system automatically recalculates projected revenue:
$$\text{Projected Revenue} = \sum_{\text{SKU}} \text{New Demand Units} \times \text{Unit Retail Price}$$
  - The updated demand matrix is passed immediately to the BOM Netting engine to cascade changes.
  - Real-time client-side table filtering dynamically recalculates visible SKU count, total units, and average price.

---

#### Flow 2: Multi-Echelon BOM Netting & Material Requirements Planning (MRP)

```mermaid
flowchart LR
    A[SKU Demand Units] --> B[Bill of Materials Table]
    B --> C[Scrap & Waste Multiplier: 1 + Waste Pct]
    C --> D[Gross Material Requirement Meters]
    D --> E[Current Inventory & Inbound Orders]
    E --> F{Net Deficit?}
    F -- Net Req > 0 --> G[Trigger Procurement Optimization]
    F -- Net Req <= 0 --> H[Inventory Covered]
```

* **Business Objective**: Translate finished garment sales targets into exact linear meter requirements for 30 raw fabric types, factoring in cutting table yield loss and existing stock.
* **Calculation Engine**:
  1. **Gross Explosion**:
$$\text{Gross Requirement}_{f, t} = \sum_{s \in \text{SKUs using } f} \text{Demand}_{s, t} \times \text{UsagePerUnit}_{s, f} \times (1 + \text{ScrapRate}_{s, f})$$
  2. **Netting Formulation**:
$$\text{Net Requirement}_{f, t} = \max\left(0, \text{Gross Requirement}_{f, t} + \text{SafetyStock}_f - \text{OnHand}_f - \text{InboundReceipts}_{f, t}\right)$$
* **Operational Outputs**:
  - 450 fabric-period balance sheets.
  - Inventory coverage ratio:
$$\text{Coverage Pct} = \frac{\text{OnHand} + \text{InboundReceipts}}{\text{Gross Requirement} + \text{SafetyStock}} \times 100$$
  - Critical fabric deficit alerts.

---

#### Flow 3: Mixed-Integer Linear Programming (MILP) Sourcing Optimization

```mermaid
flowchart TD
    A[Fabric Net Requirements: 30 Types] --> B[PuLP MILP Sourcing Solver]
    C[Supplier Master: 8 Vendors] --> B
    D[Pricing Matrix: 150 Vendor-Fabric Pairs] --> B
    E[Contractual Constraints: MOQs, Alloc Bands] --> B
    
    B --> F[Minimize Objective Function]
    F --> G[Purchase Cost + Risk Penalty + Delay Cost]
    
    G --> H[Optimized Procurement Schedule]
    H --> I[Order Allocation by Supplier]
    H --> J[MOQ Batch Compliance & Overbuy]
    H --> K[Backward PO Release Week: Delivery Week - Lead Time]
```

* **Business Objective**: Allocate raw fabric order volumes across 8 global textile mills to minimize total landed cost and operational disruption risk while strictly respecting Minimum Order Quantities (MOQ) and delivery lead times.
* **Mathematical Formulation**:
  - **Decision Variables**:
    - $x_{s, f, t} \ge 0$: Continuous volume (meters) ordered from supplier $s$ for fabric $f$ in period $t$.
    - $y_{s, f, t} \in \{0, 1\}$: Binary indicator whether an order is placed ($y = 1$) or not ($y = 0$).
  - **Objective Function**:
$$\min Z = \sum_{s, f, t} \left( \text{Price}_{s, f} \cdot x_{s, f, t} + \lambda_{\text{risk}} \cdot \text{RiskScore}_s \cdot x_{s, f, t} + \lambda_{\text{delay}} \cdot \text{LeadTimeVariance}_s \cdot x_{s, f, t} \right)$$
  - **Subject to Constraints**:
    1. **Demand Satisfaction**: $\sum_{s} x_{s, f, t} \ge \text{Net Requirement}_{f, t} \quad \forall f, t$
    2. **Minimum Order Quantity (MOQ)**: $\text{MOQ}_{s, f} \cdot y_{s, f, t} \le x_{s, f, t} \le \text{MaxCapacity}_{s, f, t} \cdot y_{s, f, t} \quad \forall s, f, t$
    3. **Supplier Allocation Banding**: $\text{MinAllocPct}_{s, f} \cdot \sum_i x_{i, f, t} \le x_{s, f, t} \le \text{MaxAllocPct}_{s, f} \cdot \sum_i x_{i, f, t}$
* **Lead Time Backward Scheduling**:
$$\text{PO Release Week} = \text{Target Delivery Week} - \text{Supplier Lead Time Weeks}$$
* **Interactive Sourcing & Live MOQ Validation**:
  - Sourcing sliders calculate allocated meters in real time: $\text{AllocatedMeters}_s = \text{NetRequirement} \times (\text{SliderPct}_s / 100)$.
  - If $\text{AllocatedMeters}_s > 0$ and $\text{AllocatedMeters}_s < \text{MOQ}_s$, a visual `⚠️ Sub-MOQ` badge is triggered.
  - Sourcing interface includes a live summary banner displaying Net Required Meters, Standard Lead Time, and Allocated Share.
  - Universal PO modal supports 1-click **"Download PO (CSV)"** and **"Copy Summary"** actions.

---

#### Flow 4: Plant Production Capacity Scheduling & Dynamic Line Balancing

```mermaid
sequenceDiagram
    autonumber
    participant Engine as Capacity Engine
    participant PlantP3 as Plant P003 (Primary Assembly)
    participant PlantP4 as Plant P004 (Flex Line)
    actor ProdLead as Production Lead

    Engine->>PlantP3: Evaluate scheduled units vs. max single-shift capacity (12,000 units)
    PlantP3-->>Engine: Scheduled: 13,440 units (Utilization = 112.0% OVERLOAD)
    Engine-->>ProdLead: Trigger critical bottleneck alert for P003 in Week 6
    ProdLead->>Engine: Authorize line rebalancing: Shift 1,440 units to Plant P004
    Engine->>PlantP3: Deduct 1,440 units (New Utilization = 100.0%)
    Engine->>PlantP4: Add 1,440 units (New Utilization = 90.7%)
    Engine-->>ProdLead: Feasibility confirmed: Both plants within 100% capacity limit
```

* **Business Objective**: Match garment assembly schedules with plant capabilities across 5 manufacturing hubs, preventing line overloads and avoiding costly emergency air freight.
* **Utilization Formula**:
$$\text{Utilization Pct} = \frac{\text{Allocated Units}}{\text{Max Units Capacity}} \times 100$$
* **Capacity Status Classification**:
  - `OPTIMAL`: $\text{Utilization} \le 85.0\%$
  - `WARNING`: $85.0\% < \text{Utilization} \le 100.0\%$
  - `OVERLOADED`: $\text{Utilization} > 100.0\%$
* **Inter-Plant Shifting Rule**: When a plant exceeds 100%, volume can be shifted to designated flex-capacity plants (`P004` or `P005`) up to their available slack.
* **Persistent Disk Synchronization**: Authorized shifts atomically write updated capacities to `plant_production_capacity.csv` ensuring persistence across server restarts.

---

#### Flow 5: In-Season Sell-Through Velocity Monitoring & Dynamic Markdowns

```mermaid
flowchart TD
    A[POS Sales Feeds: Weeks 1-6] --> B[Compute Mean Sell-Through Rate]
    B --> C[Compute Weeks of Stock: On-Hand / Average Weekly Sales]
    
    C --> D{WOS & Sell-Through Thresholds}
    
    D -- Sell-Through >= 75% OR WOS < 4.0 --> E[Classify: FAST MOVER]
    E --> F[Generate Stockout Vulnerability Alert]
    F --> G[Prioritize Warehouse Replenishment & Inbound Expediting]
    
    D -- Sell-Through <= 45% AND WOS > 8.0 --> H[Classify: SLOW MOVER]
    H --> I[Generate Critical Excess Inventory Alert]
    I --> J[Run Dynamic Markdown Elasticity Model]
    J --> K[Recommend Clearance Discount: 15% to 50%]
    K --> L[Calculate Capital Recovered & Velocity Lift]
```

* **Business Objective**: Respond to in-season selling trends during the 6-week window to prevent stockouts on fast sellers and accelerate cash recovery on slow-moving styles before season end.
* **Weeks of Stock (WOS) Calculation**:
$$\text{Weeks of Stock (WOS)} = \frac{\text{Current On-Hand Stock Units}}{\text{Average Weekly Sales Units}}$$
* **Dynamic Markdown Elasticity Model**:
$$\text{Clearance Ratio} = \min\left(1.0, 0.20 + (\text{Discount Depth Pct} \times 0.016)\right)$$
$$\text{Units Cleared} = \text{Excess Inventory Units} \times \text{Clearance Ratio}$$
$$\text{Recovered Capital} = \text{Units Cleared} \times \left(\text{Unit Cost} \times (1 - \text{Discount Depth Pct})\right)$$
$$\text{Velocity Lift} = (\text{Clearance Ratio} - 0.20) \times 450\%$$

---

#### Flow 6: DC-to-Store Logistics & Service Level Execution

* **Business Objective**: Maintain balanced stock across 4 regional DCs and optimize store replenishment lanes.
* **Logistics KPIs Monitored**:
  - DC Inventory Aging: Alerts triggered for styles aged $>45\text{ days}$.
  - Transport Lead Time: 1 to 6 days depending on lane distance.
  - Freight Cost per Unit: $1.20 to $4.80.
  - Target Service Level: $\ge 95\%$ On-Time In-Full (OTIF).

---

#### Flow 7: Consolidated Financial Waterfall Reconciliation

```mermaid
flowchart LR
    A[Gross Sales Revenue: +$53.48M] --> B[Material COGS: -$25.58M]
    B --> C[Logistics & Freight: -$4.39M]
    C --> D[Markdown Erosion: -$5.84M]
    D --> E[Consensus Gross Margin: $17.67M (33.0%)]
```

* **Business Objective**: Bridge commercial top-line aspirations with bottom-line gross margin hurdles.
* **Financial Formulas**:
$$\text{Gross Revenue} = \sum (\text{Forecasted Units} \times \text{Unit MSRP})$$
$$\text{Net Gross Margin} = \text{Gross Revenue} - \text{Material COGS} - \text{Logistics Freight} - \text{Markdown Erosion}$$
$$\text{Gross Margin Pct} = \frac{\text{Net Gross Margin}}{\text{Gross Revenue}} \times 100$$
* **Hurdle Constraint**: S&OP plans must achieve a minimum consensus gross margin hurdle of **30.0%**. Current baseline delivers **33.0%**.

---

#### Flow 8: 5-Stage Monthly S&OP Consensus Cadence & Governance

```mermaid
stateDiagram-v2
    [*] --> DEMAND_REVIEW : Week 1
    DEMAND_REVIEW --> SUPPLY_REVIEW : Demand Signed Off
    SUPPLY_REVIEW --> FINANCIAL_REVIEW : Supply Feasibility Locked
    FINANCIAL_REVIEW --> EXECUTIVE_REVIEW : P&L Margin Reconciled
    EXECUTIVE_REVIEW --> EXECUTION : Executive Chair Approval
    EXECUTION --> [*] : Plan Committed to Production & ERP
```

* **Cadence Stages**:
  1. **Demand Review**: Merchandising signs off unconstrained sales forecast and promotional plans.
  2. **Supply Review**: Procurement and Production validate fabric arrivals and plant capacities.
  3. **Financial Review**: Finance validates COGS, logistics expenses, markdown impacts, and gross margin hurdle.
  4. **Executive Review**: Executive S&OP Chair evaluates strategic trade-offs using What-If simulator (includes 1-click **"Reset to Baseline"** capability).
  5. **Execution & Lock**: Authorized decisions logged with tamper-evident audit timestamps and released to ERP/MES.
