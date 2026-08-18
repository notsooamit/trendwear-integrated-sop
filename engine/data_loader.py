"""
TrendWear S&OP Data Loader
Loads and validates all relational CSV datasets from the data directory.
"""

import os
import sqlite3
import pandas as pd
from typing import Dict, List, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(DATA_DIR, "outputs")
DB_PATH = os.path.join(DATA_DIR, "trendwear_sop.db")
os.makedirs(OUTPUT_DIR, exist_ok=True)


class DataLoader:
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        self.db_path = os.path.join(self.data_dir, "trendwear_sop.db")
        self._cache: Dict[str, pd.DataFrame] = {}

    def get_db_connection(self) -> sqlite3.Connection:
        """Returns a live sqlite3 connection to the data/trendwear_sop.db database."""
        return sqlite3.connect(self.db_path)

    def query_sql(self, query: str, params: tuple = ()) -> pd.DataFrame:
        """Executes a SQL query directly against the SQLite database and returns a DataFrame."""
        with self.get_db_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def get_table(self, relative_path: str) -> pd.DataFrame:
        if relative_path not in self._cache:
            full_path = os.path.join(self.data_dir, relative_path)
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"Dataset not found: {full_path}")
            self._cache[relative_path] = pd.read_csv(full_path)
        return self._cache[relative_path].copy()

    def reload_all(self):
        self._cache.clear()

    # Convenience accessors
    @property
    def sku_master(self) -> pd.DataFrame:
        return self.get_table(os.path.join("master", "sku_master.csv"))

    @property
    def fabric_master(self) -> pd.DataFrame:
        return self.get_table(os.path.join("master", "fabric_master.csv"))

    @property
    def supplier_master(self) -> pd.DataFrame:
        return self.get_table(os.path.join("master", "supplier_master.csv"))

    @property
    def supplier_pricing(self) -> pd.DataFrame:
        return self.get_table(os.path.join("master", "supplier_material_pricing.csv"))

    @property
    def supplier_contracts(self) -> pd.DataFrame:
        return self.get_table(os.path.join("master", "supplier_contracts.csv"))

    @property
    def supplier_capacity(self) -> pd.DataFrame:
        return self.get_table(os.path.join("master", "supplier_capacity.csv"))

    @property
    def plant_master(self) -> pd.DataFrame:
        return self.get_table(os.path.join("master", "plant_master.csv"))

    @property
    def bom_material(self) -> pd.DataFrame:
        return self.get_table(os.path.join("master", "bom_material.csv"))

    @property
    def seasonal_demand(self) -> pd.DataFrame:
        return self.get_table(os.path.join("demand", "seasonal_sku_demand.csv"))

    @property
    def current_inventory(self) -> pd.DataFrame:
        return self.get_table(os.path.join("inventory", "current_inventory.csv"))

    @property
    def plant_capacity(self) -> pd.DataFrame:
        return self.get_table(os.path.join("production", "plant_production_capacity.csv"))

    @property
    def fabric_constraints(self) -> pd.DataFrame:
        return self.get_table(os.path.join("production", "fabric_constraints.csv"))

    @property
    def historical_sell_through(self) -> pd.DataFrame:
        return self.get_table(os.path.join("sales", "historical_sell_through.csv"))

    @property
    def historical_markdowns(self) -> pd.DataFrame:
        return self.get_table(os.path.join("sales", "historical_markdowns.csv"))

    @property
    def logistics(self) -> pd.DataFrame:
        return self.get_table(os.path.join("logistics", "dc_to_store_logistics.csv"))
