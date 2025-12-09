-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. PROFILES (Extends Supabase Auth)
-- Note: Supabase handles users in auth.users. This table links to it.
CREATE TABLE IF NOT EXISTS profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  full_name TEXT,
  company_name TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. PROJECTS
CREATE TABLE IF NOT EXISTS projects (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  name TEXT NOT NULL,
  status TEXT DEFAULT 'draft', -- draft, active, archived
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. PARTS
CREATE TABLE IF NOT EXISTS parts (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  file_url TEXT NOT NULL, -- Supabase Storage URL
  volume_mm3 FLOAT,
  surface_area_mm2 FLOAT,
  bbox JSONB, -- {x: 10, y: 20, z: 30}
  uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. MATERIALS
CREATE TABLE IF NOT EXISTS materials (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT NOT NULL, -- 'Thermoplastic', 'Thermoset'
  density_g_cm3 FLOAT NOT NULL,
  melt_temp_c FLOAT NOT NULL,
  mold_temp_c FLOAT NOT NULL,
  thermal_conductivity FLOAT, -- W/mK
  specific_heat FLOAT, -- J/kgK
  shrinkage_rate FLOAT, -- Percentage (0.01 = 1%)
  viscosity_index FLOAT DEFAULT 1.0, -- Relative flow factor (1.0 = water-like... roughly)
  description TEXT
);

-- 5. SIMULATIONS
CREATE TABLE IF NOT EXISTS simulations (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  part_id UUID REFERENCES parts(id) ON DELETE CASCADE,
  material_id UUID REFERENCES materials(id),
  status TEXT DEFAULT 'pending', -- pending, processing, completed, failed
  results JSONB, -- The massive JSON blob of results
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- SEED DATA: MATERIALS
INSERT INTO materials (name, type, density_g_cm3, melt_temp_c, mold_temp_c, thermal_conductivity, specific_heat, shrinkage_rate, viscosity_index) VALUES
('PP (Polypropylene)', 'Thermoplastic', 0.905, 230, 40, 0.12, 1900, 0.015, 1.0),
('ABS (Generic)', 'Thermoplastic', 1.04, 230, 60, 0.18, 1400, 0.006, 1.2),
('PA6 (Nylon 6)', 'Thermoplastic', 1.13, 260, 80, 0.25, 1600, 0.012, 0.9),
('PC (Polycarbonate)', 'Thermoplastic', 1.20, 300, 90, 0.20, 1200, 0.007, 2.5),
('POM (Acetal)', 'Thermoplastic', 1.41, 190, 90, 0.23, 1470, 0.020, 1.1),
('LDPE', 'Thermoplastic', 0.92, 210, 40, 0.33, 2300, 0.020, 0.8),
('HDPE', 'Thermoplastic', 0.95, 220, 40, 0.45, 2300, 0.025, 0.9),
('PS (Polystyrene)', 'Thermoplastic', 1.05, 220, 50, 0.13, 1300, 0.004, 1.1),
('PVC (Rigid)', 'Thermoplastic', 1.40, 180, 40, 0.16, 1000, 0.004, 3.0),
('PMMA (Acrylic)', 'Thermoplastic', 1.18, 240, 60, 0.19, 1450, 0.004, 2.0),
('PBT', 'Thermoplastic', 1.31, 260, 70, 0.21, 1500, 0.018, 1.0),
('PET', 'Thermoplastic', 1.38, 270, 100, 0.24, 1200, 0.015, 1.1),
('ASA', 'Thermoplastic', 1.07, 250, 60, 0.17, 1350, 0.005, 1.3),
('SAN', 'Thermoplastic', 1.08, 230, 60, 0.14, 1300, 0.004, 1.4),
('TPE (Generic)', 'Thermoplastic', 1.10, 190, 30, 0.10, 2000, 0.015, 4.0),
('TPU (95A)', 'Thermoplastic', 1.20, 200, 40, 0.18, 1700, 0.012, 3.5),
('PLA (Biodegradable)', 'Thermoplastic', 1.24, 190, 30, 0.13, 1800, 0.004, 1.5),
('PEEK (High Temp)', 'Thermoplastic', 1.32, 380, 180, 0.25, 2200, 0.010, 5.0);

-- Row Level Security (RLS) - Basic Policy
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE parts ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulations ENABLE ROW LEVEL SECURITY;

-- Note: We will add specific policies later (e.g., "Users can only see their own projects")
-- For now, allow everything for authenticated users to facilitate development
CREATE POLICY "Enable all access for authenticated users" ON projects FOR ALL TO authenticated USING (true);
CREATE POLICY "Enable all access for authenticated users" ON parts FOR ALL TO authenticated USING (true);
CREATE POLICY "Enable all access for authenticated users" ON simulations FOR ALL TO authenticated USING (true);
