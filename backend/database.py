import json
import os
import uuid
import datetime

# Mock DB File Path
MOCK_DB_FILE = os.path.join(os.path.dirname(__file__), "mock_db.json")

class MockSupabaseClient:
    def __init__(self):
        self.data = self._load_db()
        print(f"[MOCK DB] Loaded Data. Materials: {len(self.data.get('materials', []))}")

    def _load_db(self):
        if not os.path.exists(MOCK_DB_FILE):
             print("[MOCK DB] Creating new mock database...")
             initial_data = {
                 "projects": [],
                 "parts": [],
                 "simulations": [],
                 "materials": self._seed_materials()
             }
             self._save_db(initial_data)
             return initial_data
        
        try:
            with open(MOCK_DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"projects": [], "parts": [], "simulations": [], "materials": []}
            
    def _save_db(self, data):
        with open(MOCK_DB_FILE, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def _seed_materials(self):
        # Full 18 Standard Materials
        return [
            {"id": str(uuid.uuid4()), "name": "PP (Polypropylene)", "density_g_cm3": 0.905, "melt_temp_c": 230, "mold_temp_c": 40, "shrinkage": 0.015},
            {"id": str(uuid.uuid4()), "name": "ABS (Generic)", "density_g_cm3": 1.04, "melt_temp_c": 230, "mold_temp_c": 60, "shrinkage": 0.006},
            {"id": str(uuid.uuid4()), "name": "PA6 (Nylon 6)", "density_g_cm3": 1.13, "melt_temp_c": 260, "mold_temp_c": 80, "shrinkage": 0.012},
            {"id": str(uuid.uuid4()), "name": "PC (Polycarbonate)", "density_g_cm3": 1.20, "melt_temp_c": 300, "mold_temp_c": 90, "shrinkage": 0.007},
            {"id": str(uuid.uuid4()), "name": "POM (Acetal)", "density_g_cm3": 1.41, "melt_temp_c": 190, "mold_temp_c": 90, "shrinkage": 0.020},
            {"id": str(uuid.uuid4()), "name": "LDPE", "density_g_cm3": 0.92, "melt_temp_c": 210, "mold_temp_c": 40, "shrinkage": 0.020},
            {"id": str(uuid.uuid4()), "name": "HDPE", "density_g_cm3": 0.95, "melt_temp_c": 220, "mold_temp_c": 40, "shrinkage": 0.025},
            {"id": str(uuid.uuid4()), "name": "PS (Polystyrene)", "density_g_cm3": 1.05, "melt_temp_c": 220, "mold_temp_c": 50, "shrinkage": 0.004},
            {"id": str(uuid.uuid4()), "name": "PVC (Rigid)", "density_g_cm3": 1.40, "melt_temp_c": 180, "mold_temp_c": 40, "shrinkage": 0.004},
            {"id": str(uuid.uuid4()), "name": "PMMA (Acrylic)", "density_g_cm3": 1.18, "melt_temp_c": 240, "mold_temp_c": 60, "shrinkage": 0.004},
            {"id": str(uuid.uuid4()), "name": "PBT", "density_g_cm3": 1.31, "melt_temp_c": 260, "mold_temp_c": 70, "shrinkage": 0.018},
            {"id": str(uuid.uuid4()), "name": "PET", "density_g_cm3": 1.38, "melt_temp_c": 270, "mold_temp_c": 100, "shrinkage": 0.015},
            {"id": str(uuid.uuid4()), "name": "ASA", "density_g_cm3": 1.07, "melt_temp_c": 250, "mold_temp_c": 60, "shrinkage": 0.005},
            {"id": str(uuid.uuid4()), "name": "SAN", "density_g_cm3": 1.08, "melt_temp_c": 230, "mold_temp_c": 60, "shrinkage": 0.004},
            {"id": str(uuid.uuid4()), "name": "TPE (Generic)", "density_g_cm3": 1.10, "melt_temp_c": 190, "mold_temp_c": 30, "shrinkage": 0.015},
            {"id": str(uuid.uuid4()), "name": "TPU (95A)", "density_g_cm3": 1.20, "melt_temp_c": 200, "mold_temp_c": 40, "shrinkage": 0.012},
            {"id": str(uuid.uuid4()), "name": "PLA (Biodegradable)", "density_g_cm3": 1.24, "melt_temp_c": 190, "mold_temp_c": 30, "shrinkage": 0.004},
            {"id": str(uuid.uuid4()), "name": "PEEK (High Temp)", "density_g_cm3": 1.32, "melt_temp_c": 380, "mold_temp_c": 180, "shrinkage": 0.010}
        ]

    def table(self, table_name):
        return MockTableQuery(self, table_name)

class MockTableQuery:
    def __init__(self, client, table):
        self.client = client
        self.table = table
        self.filters = []
        self.limit_val = None
        self.pending_insert = None

    def select(self, columns="*"):
        return self 

    def insert(self, record):
        self.pending_insert = record
        return self

    def eq(self, column, value):
        self.filters.append((column, value))
        return self

    def limit(self, count):
        self.limit_val = count
        return self

    def execute(self):
        # Handle Insert
        if self.pending_insert:
            record = self.pending_insert
            if "id" not in record:
                record["id"] = str(uuid.uuid4())
            record["created_at"] = datetime.datetime.now().isoformat()
            
            self.client.data.setdefault(self.table, []).append(record)
            self.client._save_db(self.client.data)
            return MockResponse([record])

        # Handle Select
        rows = self.client.data.get(self.table, [])
        
        # Apply Filters
        for col, val in self.filters:
            rows = [r for r in rows if str(r.get(col)) == str(val)]
            
        # Apply Limit
        if self.limit_val:
            rows = rows[:self.limit_val]
            
        return MockResponse(rows)

class MockResponse:
    def __init__(self, data):
        self.data = data

# Initialize Mock Client
supabase = MockSupabaseClient()

def get_db():
    return supabase
