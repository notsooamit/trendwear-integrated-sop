"""
SQLite Database Builder for TrendWear S&OP Enterprise Suite
Imports all 20 CSV datasets into a relational SQLite database (data/trendwear_sop.db).
"""

import os
import glob
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "trendwear_sop.db")


def build_sqlite_database():
    print(f"Initializing SQLite Database at: {DB_PATH}")
    
    # Remove existing DB if present to rebuild cleanly
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception:
            pass

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Discover all CSV files
    all_csv_files = glob.glob(os.path.join(DATA_DIR, "**", "*.csv"), recursive=True)
    
    loaded_tables = []
    total_records = 0

    for csv_file in sorted(all_csv_files):
        table_name = os.path.splitext(os.path.basename(csv_file))[0]
        category = os.path.basename(os.path.dirname(csv_file))
        
        df = pd.read_csv(csv_file)
        
        # Write to SQLite
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        
        row_count = len(df)
        total_records += row_count
        loaded_tables.append((category, table_name, row_count))
        print(f"  [+] Imported '{category}/{table_name}.csv' -> Table: {table_name} ({row_count:,} rows)")

    # Create helpful indexes for foreign keys
    indexes = [
        ("idx_sku_master_sku", "sku_master", "sku_id"),
        ("idx_fabric_master_fab", "fabric_master", "fabric_id"),
        ("idx_supplier_master_sup", "supplier_master", "supplier_id"),
        ("idx_plant_master_plant", "plant_master", "plant_id"),
        ("idx_seasonal_demand_sku_period", "seasonal_sku_demand", "sku_id, period"),
        ("idx_bom_sku_fab", "bom_material", "sku_id, fabric_id"),
        ("idx_pricing_sup_fab", "supplier_material_pricing", "supplier_id, fabric_id"),
        ("idx_mrp_fab_period", "material_requirements", "fabric_id, period"),
        ("idx_po_plan_fab_sup", "optimized_procurement_plan", "fabric_id, supplier_id")
    ]

    for idx_name, tbl, cols in indexes:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {tbl} ({cols});")
        except Exception as e:
            # Table might not exist or column might differ
            pass

    conn.commit()
    conn.close()

    print("\n============================================================")
    print(f" SUCCESS: SQLite Database generated with {len(loaded_tables)} tables ({total_records:,} total records)")
    print(f" Database file location: {DB_PATH}")
    print("============================================================")
    return loaded_tables


if __name__ == "__main__":
    build_sqlite_database()
