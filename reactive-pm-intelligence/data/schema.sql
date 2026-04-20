CREATE TABLE IF NOT EXISTS work_orders_seed (
    work_order_id TEXT PRIMARY KEY,
    asset_id TEXT,
    location_id TEXT,
    problem_code TEXT,
    problem_description TEXT,
    created_date TEXT,
    closed_date TEXT,
    technician_id TEXT,
    priority TEXT,
    cost REAL,
    resolution_code TEXT,
    asset_category TEXT,
    asset_age_category TEXT,
    resolution_hours REAL,
    season_flag TEXT
);

CREATE TABLE IF NOT EXISTS facilities_seed (
    location_id TEXT PRIMARY KEY,
    facility_name TEXT,
    city TEXT,
    region TEXT,
    country TEXT,
    property_type TEXT,
    gross_area_sqft INTEGER,
    criticality_tier TEXT,
    occupancy_band TEXT
);

CREATE TABLE IF NOT EXISTS assets_seed (
    asset_id TEXT PRIMARY KEY,
    location_id TEXT,
    asset_name TEXT,
    asset_category TEXT,
    manufacturer TEXT,
    model_number TEXT,
    install_date TEXT,
    health_index REAL,
    service_level TEXT,
    criticality_rank TEXT
);

CREATE TABLE IF NOT EXISTS technicians_seed (
    technician_id TEXT PRIMARY KEY,
    technician_name TEXT,
    primary_skill TEXT,
    region TEXT,
    shift TEXT
);
