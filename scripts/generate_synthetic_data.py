"""
TrendWear S&OP - Synthetic Dataset Generator
Generates all 15 relational datasets with seeded business scenarios:
1. Low-performing supplier S004 (High risk, 72% OTD, 7 wk lead time, -4% price)
2. Critical fabric FAB_014 (6-week lead time)
3. Plant P003 bottleneck (108% capacity utilization in Week 6)
4. Jackets 50% demand spike in Week 6
5. Fast mover SKU_021 (Stock-out risk, WOS = 2.1)
6. Slow mover SKU_037 (Excess inventory, WOS = 18.5)
"""

import os
import random
import numpy as np
import pandas as pd

# Set deterministic seed for reproducibility
np.random.seed(42)
random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

DIRS = [
    os.path.join(DATA_DIR, "master"),
    os.path.join(DATA_DIR, "demand"),
    os.path.join(DATA_DIR, "inventory"),
    os.path.join(DATA_DIR, "production"),
    os.path.join(DATA_DIR, "sales"),
    os.path.join(DATA_DIR, "logistics"),
]

for d in DIRS:
    os.makedirs(d, exist_ok=True)

# -------------------------------------------------------------
# 1. Master Data: sku_master.csv (50 SKUs)
# -------------------------------------------------------------
categories = ["Jackets", "Shirts", "Trousers", "Dresses", "Activewear", "Outerwear"]
category_skus = {
    "Jackets": [f"SKU_{i:03d}" for i in range(1, 10)],       # SKU_001 - SKU_009
    "Shirts": [f"SKU_{i:03d}" for i in range(10, 20)],       # SKU_010 - SKU_019
    "Trousers": [f"SKU_{i:03d}" for i in range(20, 28)],     # SKU_020 - SKU_027 (SKU_021 fast mover)
    "Dresses": [f"SKU_{i:03d}" for i in range(28, 36)],      # SKU_028 - SKU_035
    "Activewear": [f"SKU_{i:03d}" for i in range(36, 44)],   # SKU_036 - SKU_043 (SKU_037 slow mover)
    "Outerwear": [f"SKU_{i:03d}" for i in range(44, 51)],    # SKU_044 - SKU_050
}

sku_rows = []
price_ranges = {
    "Jackets": (89.0, 169.0),
    "Shirts": (39.0, 79.0),
    "Trousers": (49.0, 99.0),
    "Dresses": (69.0, 139.0),
    "Activewear": (35.0, 85.0),
    "Outerwear": (119.0, 229.0),
}

for cat, skus in category_skus.items():
    for sku in skus:
        min_p, max_p = price_ranges[cat]
        price = round(random.uniform(min_p, max_p), 2)
        margin = round(random.uniform(0.48, 0.62), 3)
        launch_wk = random.choice([1, 2, 3, 4])
        status = "Active"
        if sku in ["SKU_009", "SKU_050"]:
            status = "New"
        elif sku in ["SKU_037", "SKU_019"]:
            status = "Phase-Out"

        sku_rows.append({
            "sku_id": sku,
            "sku_name": f"TrendWear {cat[:-1] if cat.endswith('s') else cat} {sku[-3:]}",
            "category": cat,
            "season": "FW26" if cat in ["Jackets", "Outerwear"] else "SS26",
            "region_group": "Global",
            "unit_retail_price": price,
            "unit_target_margin": margin,
            "launch_week": launch_wk,
            "lifecycle_status": status
        })

df_sku = pd.DataFrame(sku_rows)
df_sku.to_csv(os.path.join(DATA_DIR, "master", "sku_master.csv"), index=False)

# -------------------------------------------------------------
# 2. Master Data: fabric_master.csv (30 Fabrics)
# -------------------------------------------------------------
fabric_types = ["Cotton", "Wool", "Polyester", "Denim", "Linen", "Silk", "Nylon", "Poly-Blend"]
fabric_rows = []
for i in range(1, 31):
    fid = f"FAB_{i:03d}"
    ftype = random.choice(fabric_types)
    cost = round(random.uniform(5.5, 24.0), 2)
    lead_time = random.choice([3, 4, 5])
    safety_stock = random.randint(2000, 6000)
    criticality = random.choice(["LOW", "MEDIUM", "HIGH"])
    
    # Specific seeded constraint: FAB_014 is high criticality, 6-week lead time
    if fid == "FAB_014":
        ftype = "Wool-Blend"
        cost = 18.50
        lead_time = 6
        safety_stock = 7500
        criticality = "HIGH"
    elif fid in ["FAB_001", "FAB_002", "FAB_008"]:
        criticality = "HIGH"

    fabric_rows.append({
        "fabric_id": fid,
        "fabric_name": f"Premium {ftype} Grade-{i}",
        "fabric_type": ftype,
        "standard_cost_per_meter": cost,
        "standard_lead_time_weeks": lead_time,
        "safety_stock_meters": safety_stock,
        "criticality": criticality
    })

df_fabric = pd.DataFrame(fabric_rows)
df_fabric.to_csv(os.path.join(DATA_DIR, "master", "fabric_master.csv"), index=False)

# -------------------------------------------------------------
# 3. Master Data: supplier_master.csv (8 Suppliers)
# -------------------------------------------------------------
supplier_rows = [
    {"supplier_id": "S001", "supplier_name": "Apex Textile Mills", "supplier_status": "Active", "base_risk_factor": 0.12, "quality_score": 0.97, "otd_score": 0.96, "average_lead_time_weeks": 4, "lead_time_variability_weeks": 0.4, "financial_risk_score": 0.10, "capacity_tier": "Tier-1", "risk_category": "LOW"},
    {"supplier_id": "S002", "supplier_name": "Global Weavers Ltd", "supplier_status": "Active", "base_risk_factor": 0.18, "quality_score": 0.95, "otd_score": 0.93, "average_lead_time_weeks": 4, "lead_time_variability_weeks": 0.6, "financial_risk_score": 0.15, "capacity_tier": "Tier-1", "risk_category": "LOW"},
    {"supplier_id": "S003", "supplier_name": "Oriental Fabric Corp", "supplier_status": "Active", "base_risk_factor": 0.32, "quality_score": 0.91, "otd_score": 0.89, "average_lead_time_weeks": 5, "lead_time_variability_weeks": 1.1, "financial_risk_score": 0.28, "capacity_tier": "Tier-2", "risk_category": "MEDIUM"},
    {"supplier_id": "S004", "supplier_name": "Budget FastTex Industries", "supplier_status": "Active", "base_risk_factor": 0.68, "quality_score": 0.81, "otd_score": 0.72, "average_lead_time_weeks": 7, "lead_time_variability_weeks": 2.3, "financial_risk_score": 0.58, "capacity_tier": "Tier-1", "risk_category": "HIGH"},
    {"supplier_id": "S005", "supplier_name": "EuroKnit Premium", "supplier_status": "Active", "base_risk_factor": 0.08, "quality_score": 0.98, "otd_score": 0.98, "average_lead_time_weeks": 3, "lead_time_variability_weeks": 0.2, "financial_risk_score": 0.05, "capacity_tier": "Tier-2", "risk_category": "LOW"},
    {"supplier_id": "S006", "supplier_name": "Pacific Spinners", "supplier_status": "Active", "base_risk_factor": 0.38, "quality_score": 0.88, "otd_score": 0.84, "average_lead_time_weeks": 5, "lead_time_variability_weeks": 1.4, "financial_risk_score": 0.35, "capacity_tier": "Tier-2", "risk_category": "MEDIUM"},
    {"supplier_id": "S007", "supplier_name": "Vanguard Textiles", "supplier_status": "Active", "base_risk_factor": 0.22, "quality_score": 0.93, "otd_score": 0.91, "average_lead_time_weeks": 4, "lead_time_variability_weeks": 0.7, "financial_risk_score": 0.20, "capacity_tier": "Tier-2", "risk_category": "LOW"},
    {"supplier_id": "S008", "supplier_name": "Southern Mill Co.", "supplier_status": "Active", "base_risk_factor": 0.35, "quality_score": 0.90, "otd_score": 0.88, "average_lead_time_weeks": 5, "lead_time_variability_weeks": 1.2, "financial_risk_score": 0.30, "capacity_tier": "Tier-3", "risk_category": "MEDIUM"},
]

df_supplier = pd.DataFrame(supplier_rows)
df_supplier.to_csv(os.path.join(DATA_DIR, "master", "supplier_master.csv"), index=False)

# -------------------------------------------------------------
# 4. Master Data: supplier_material_pricing.csv & supplier_contracts.csv
# -------------------------------------------------------------
pricing_rows = []
contract_rows = []

for _, f_row in df_fabric.iterrows():
    fid = f_row["fabric_id"]
    base_cost = f_row["standard_cost_per_meter"]
    
    # Assign 3 to 5 suppliers per fabric
    selected_suppliers = ["S001", "S002", "S004"] + random.sample(["S003", "S005", "S006", "S007", "S008"], 2)
    for sid in selected_suppliers:
        # S004 is 4% to 8% cheaper
        if sid == "S004":
            discount = random.uniform(0.04, 0.08)
            price = round(base_cost * (1 - discount), 2)
        elif sid == "S005":
            premium = random.uniform(0.05, 0.12)
            price = round(base_cost * (1 + premium), 2)
        else:
            variation = random.uniform(-0.03, 0.04)
            price = round(base_cost * (1 + variation), 2)
            
        pricing_rows.append({
            "supplier_id": sid,
            "fabric_id": fid,
            "price_per_meter": price,
            "currency": "USD",
            "price_valid_from": "2026-01-01",
            "price_valid_to": "2026-12-31"
        })
        
        # Contract MOQ & Allocation
        moq = 5000 if fid == "FAB_014" else random.choice([2500, 3000, 4000, 5000])
        min_alloc = 0.15 if sid in ["S001", "S002"] else 0.10
        max_alloc = 0.60 if sid in ["S001", "S002"] else 0.40
        if sid == "S004":
            max_alloc = 0.80 # Historically high allocation before optimization
            
        contract_rows.append({
            "supplier_id": sid,
            "fabric_id": fid,
            "minimum_allocation_pct": min_alloc,
            "maximum_allocation_pct": max_alloc,
            "minimum_order_qty_meters": moq,
            "contract_expiry_date": "2026-12-31",
            "committed_volume_meters": 50000
        })

df_pricing = pd.DataFrame(pricing_rows)
df_pricing.to_csv(os.path.join(DATA_DIR, "master", "supplier_material_pricing.csv"), index=False)

df_contracts = pd.DataFrame(contract_rows)
df_contracts.to_csv(os.path.join(DATA_DIR, "master", "supplier_contracts.csv"), index=False)

# -------------------------------------------------------------
# 5. Master Data: supplier_capacity.csv (W1 - W12)
# -------------------------------------------------------------
sup_cap_rows = []
for p in range(1, 13):
    period = f"W{p:02d}"
    for _, prow in df_pricing.iterrows():
        sid = prow["supplier_id"]
        fid = prow["fabric_id"]
        max_cap = random.randint(12000, 25000)
        committed = int(max_cap * random.uniform(0.35, 0.65))
        
        # Seed constraint: S002 / FAB_014 in Week 5 is tightly constrained
        if sid == "S002" and fid == "FAB_014" and period == "W05":
            max_cap = 16000
            committed = 8000 # Leaves only 8,000 available
            
        avail = max_cap - committed
        sup_cap_rows.append({
            "supplier_id": sid,
            "fabric_id": fid,
            "period": period,
            "max_supply_meters": max_cap,
            "committed_supply_meters": committed,
            "available_supply_meters": avail
        })

df_sup_cap = pd.DataFrame(sup_cap_rows)
df_sup_cap.to_csv(os.path.join(DATA_DIR, "master", "supplier_capacity.csv"), index=False)

# -------------------------------------------------------------
# 6. Master Data: plant_master.csv (5 Plants)
# -------------------------------------------------------------
plant_rows = [
    {"plant_id": "P001", "plant_name": "Americas Hub - Plant 1", "region": "North America", "production_type": "Cut & Sew / Assembly", "weekly_capacity_units": 12000, "flex_capacity_pct": 0.15},
    {"plant_id": "P002", "plant_name": "EuroCraft Facility", "region": "Europe", "production_type": "Precision Tailoring", "weekly_capacity_units": 9500, "flex_capacity_pct": 0.10},
    {"plant_id": "P003", "plant_name": "Asia Pacific MegaPlant", "region": "Asia-Pacific", "production_type": "High Volume Apparel", "weekly_capacity_units": 18000, "flex_capacity_pct": 0.12},
    {"plant_id": "P004", "plant_name": "Latin America Production", "region": "Latin America", "production_type": "Flexible Quick-Turn", "weekly_capacity_units": 8500, "flex_capacity_pct": 0.20},
    {"plant_id": "P005", "plant_name": "South Asia Garment Hub", "region": "Asia-Pacific", "production_type": "Activewear & Tops", "weekly_capacity_units": 14000, "flex_capacity_pct": 0.15},
]
df_plant = pd.DataFrame(plant_rows)
df_plant.to_csv(os.path.join(DATA_DIR, "master", "plant_master.csv"), index=False)

# -------------------------------------------------------------
# 7. Master Data: bom_material.csv (160 Mappings)
# -------------------------------------------------------------
bom_rows = []
# Ensure every SKU uses 1-3 fabrics
for _, s_row in df_sku.iterrows():
    sku = s_row["sku_id"]
    cat = s_row["category"]
    
    # Specific primary fabrics for realism
    if cat == "Jackets":
        primary_fabric = "FAB_014" if sku in ["SKU_001", "SKU_002", "SKU_003"] else random.choice(["FAB_001", "FAB_002", "FAB_003"])
        lining_fabric = random.choice(["FAB_010", "FAB_011"])
        bom_rows.append({"sku_id": sku, "fabric_id": primary_fabric, "fabric_per_unit_meters": 2.4, "waste_pct": 0.05})
        bom_rows.append({"sku_id": sku, "fabric_id": lining_fabric, "fabric_per_unit_meters": 1.2, "waste_pct": 0.03})
    elif cat == "Outerwear":
        bom_rows.append({"sku_id": sku, "fabric_id": "FAB_014" if sku == "SKU_044" else random.choice(["FAB_004", "FAB_005"]), "fabric_per_unit_meters": 3.2, "waste_pct": 0.06})
        bom_rows.append({"sku_id": sku, "fabric_id": random.choice(["FAB_012", "FAB_013"]), "fabric_per_unit_meters": 1.5, "waste_pct": 0.04})
    elif cat == "Shirts":
        bom_rows.append({"sku_id": sku, "fabric_id": random.choice(["FAB_006", "FAB_007", "FAB_008"]), "fabric_per_unit_meters": 1.6, "waste_pct": 0.04})
    elif cat == "Trousers":
        bom_rows.append({"sku_id": sku, "fabric_id": random.choice(["FAB_015", "FAB_016", "FAB_017"]), "fabric_per_unit_meters": 1.9, "waste_pct": 0.05})
    elif cat == "Dresses":
        bom_rows.append({"sku_id": sku, "fabric_id": random.choice(["FAB_018", "FAB_019", "FAB_020"]), "fabric_per_unit_meters": 2.2, "waste_pct": 0.04})
    else: # Activewear
        bom_rows.append({"sku_id": sku, "fabric_id": random.choice(["FAB_021", "FAB_022", "FAB_023"]), "fabric_per_unit_meters": 1.4, "waste_pct": 0.03})

df_bom = pd.DataFrame(bom_rows)
df_bom.to_csv(os.path.join(DATA_DIR, "master", "bom_material.csv"), index=False)

# -------------------------------------------------------------
# 8. Demand Data: seasonal_sku_demand.csv (4,000+ Records)
# -------------------------------------------------------------
regions = ["North America", "Europe", "Asia-Pacific", "Latin America"]
demand_periods = [f"W{w:02d}" for w in range(1, 13)] + ["M04", "M05", "M06"]
demand_rows = []

for sku_row in df_sku.to_dict("records"):
    sku = sku_row["sku_id"]
    cat = sku_row["category"]
    base_demand = random.randint(300, 1100)
    
    # Fast mover SKU_021 has higher base demand
    if sku == "SKU_021":
        base_demand = 1800
    # Slow mover SKU_037 has low base demand
    elif sku == "SKU_037":
        base_demand = 220
        
    for region in regions:
        region_weight = {"North America": 0.38, "Europe": 0.32, "Asia-Pacific": 0.20, "Latin America": 0.10}[region]
        for period in demand_periods:
            wk_num = int(period[1:]) if period.startswith("W") else 12 + int(period[1:])
            
            # Seasonal / weekly shape
            seasonality = 1.0 + 0.15 * np.sin(wk_num / 2.0)
            reg_demand = int(base_demand * region_weight * seasonality * random.uniform(0.92, 1.08))
            
            # Seeded Event: Jackets demand +50% in Week 6
            if cat == "Jackets" and period == "W06":
                reg_demand = int(reg_demand * 1.50)
                
            demand_rows.append({
                "sku_id": sku,
                "region": region,
                "period": period,
                "forecasted_demand_units": max(10, reg_demand),
                "forecast_version": "v1.0",
                "forecast_confidence": round(random.uniform(0.82, 0.95), 2)
            })

df_demand = pd.DataFrame(demand_rows)
df_demand.to_csv(os.path.join(DATA_DIR, "demand", "seasonal_sku_demand.csv"), index=False)

# -------------------------------------------------------------
# 9. Inventory Data: current_inventory.csv
# -------------------------------------------------------------
dc_locations = ["DC_NA", "DC_EU", "DC_APAC", "DC_LATAM"]
inv_rows = []

for sku in df_sku["sku_id"].unique():
    for loc in dc_locations:
        stock = random.randint(300, 1500)
        reserved = int(stock * random.uniform(0.10, 0.25))
        safety = random.randint(250, 600)
        inbound = random.choice([0, 200, 500, 800])
        age = random.randint(5, 45)
        
        # Seeded Anomalies:
        # SKU_021 (Fast mover) -> very low stock (~2.1 WOS)
        if sku == "SKU_021":
            stock = 120
            safety = 500
            inbound = 150
            age = 4
        # SKU_037 (Slow mover) -> excessive stock (~18.5 WOS)
        elif sku == "SKU_037":
            stock = 2400
            safety = 200
            inbound = 0
            age = 75

        inv_rows.append({
            "sku_id": sku,
            "location_id": loc,
            "available_stock_units": stock,
            "reserved_stock_units": reserved,
            "safety_stock_threshold": safety,
            "inbound_stock_units": inbound,
            "inventory_age_days": age
        })

df_inv = pd.DataFrame(inv_rows)
df_inv.to_csv(os.path.join(DATA_DIR, "inventory", "current_inventory.csv"), index=False)

# -------------------------------------------------------------
# 10. Production Data: plant_production_capacity.csv & fabric_constraints.csv
# -------------------------------------------------------------
plant_cap_rows = []
for p_row in df_plant.to_dict("records"):
    pid = p_row["plant_id"]
    base_cap = p_row["weekly_capacity_units"]
    for w in range(1, 13):
        period = f"W{w:02d}"
        max_cap = base_cap
        maint = random.choice([0, 0, 500, 1000])
        allocated = int((max_cap - maint) * random.uniform(0.70, 0.88))
        
        # Seeded Bottleneck: Plant P003 in Week 6 is overloaded at 108%
        if pid == "P003" and period == "W06":
            allocated = int(max_cap * 1.08)
            
        avail = max(0, max_cap - maint - allocated)
        plant_cap_rows.append({
            "plant_id": pid,
            "period": period,
            "max_units_capacity": max_cap,
            "already_allocated_units": allocated,
            "maintenance_units": maint,
            "available_units": avail
        })

df_plant_cap = pd.DataFrame(plant_cap_rows)
df_plant_cap.to_csv(os.path.join(DATA_DIR, "production", "plant_production_capacity.csv"), index=False)

# Fabric constraints by plant
fab_constraint_rows = []
for fid in df_fabric["fabric_id"].unique():
    for pid in df_plant["plant_id"].unique():
        fab_constraint_rows.append({
            "fabric_id": fid,
            "plant_id": pid,
            "max_weekly_throughput_meters": random.choice([15000, 20000, 30000, 45000]),
            "processing_lead_time_weeks": random.choice([1, 2])
        })
df_fab_const = pd.DataFrame(fab_constraint_rows)
df_fab_const.to_csv(os.path.join(DATA_DIR, "production", "fabric_constraints.csv"), index=False)

# -------------------------------------------------------------
# 11. Sales & Markdown Data: historical_sell_through.csv & historical_markdowns.csv
# -------------------------------------------------------------
sell_rows = []
markdown_rows = []

for sku_row in df_sku.to_dict("records"):
    sku = sku_row["sku_id"]
    cat = sku_row["category"]
    
    # 12 historical selling weeks
    for sw in range(1, 13):
        avail = random.randint(1000, 3000)
        
        if sku == "SKU_021": # Fast mover
            sold = int(avail * random.uniform(0.82, 0.94))
        elif sku == "SKU_037": # Slow mover
            sold = int(avail * random.uniform(0.12, 0.22))
        else:
            sold = int(avail * random.uniform(0.40, 0.75))
            
        rate = round(sold / avail, 3)
        avg_weekly = round(sold / 1.0, 1)
        sell_rows.append({
            "sku_id": sku,
            "selling_week": f"W-{13-sw:02d}",
            "units_available": avail,
            "units_sold": sold,
            "sell_through_rate": rate,
            "average_weekly_sales": avg_weekly
        })
        
    # Historical markdowns response
    for disc in [0.15, 0.25, 0.35, 0.50]:
        base_s = random.randint(200, 500)
        lift_mult = {0.15: 1.25, 0.25: 1.55, 0.35: 1.95, 0.50: 2.70}[disc]
        post_s = int(base_s * lift_mult * random.uniform(0.95, 1.05))
        markdown_rows.append({
            "sku_id": sku,
            "discount_percentage": disc,
            "units_sold_before_markdown": base_s,
            "units_sold_post_markdown": post_s,
            "sell_through_lift": round((post_s - base_s) / base_s, 2)
        })

df_sell = pd.DataFrame(sell_rows)
df_sell.to_csv(os.path.join(DATA_DIR, "sales", "historical_sell_through.csv"), index=False)

df_mark = pd.DataFrame(markdown_rows)
df_mark.to_csv(os.path.join(DATA_DIR, "sales", "historical_markdowns.csv"), index=False)

# -------------------------------------------------------------
# 12. Logistics Data: dc_to_store_logistics.csv
# -------------------------------------------------------------
logistics_rows = []
for dc in dc_locations:
    for store_num in range(1, 16):
        store_id = f"STR_{dc[-2:]}_{store_num:02d}"
        logistics_rows.append({
            "dc_id": dc,
            "store_id": store_id,
            "transportation_cost_per_unit": round(random.uniform(1.20, 3.80), 2),
            "transport_lead_time_days": random.choice([2, 3, 4, 5, 6]),
            "service_level": round(random.uniform(0.96, 0.99), 3)
        })

df_log = pd.DataFrame(logistics_rows)
df_log.to_csv(os.path.join(DATA_DIR, "logistics", "dc_to_store_logistics.csv"), index=False)

print("SUCCESS: All 15 relational datasets generated successfully in 'data/' subdirectories.")
