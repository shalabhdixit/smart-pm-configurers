from __future__ import annotations

import random
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "data" / "sample_work_orders.csv"
DB_PATH = BASE_DIR / "data" / "reactive_pm.db"
SCHEMA_PATH = BASE_DIR / "data" / "schema.sql"
RANDOM_SEED = 42
RNG = np.random.default_rng(RANDOM_SEED)


@dataclass(frozen=True)
class RecurringPattern:
    asset_id: str
    location_id: str
    problem_code: str
    problem_description: str
    interval_days: int
    occurrences: int
    start_date: datetime
    asset_category: str
    asset_age_category: str
    technician_prefix: str
    base_cost: float


PROBLEM_CODES = {
    "HVAC-001": "Cooling failure",
    "HVAC-004": "Compressor short cycling",
    "HVAC-010": "Airflow imbalance",
    "PLMB-003": "Drain clog",
    "PLMB-007": "Pipe leak",
    "PLMB-010": "Restroom backup",
    "ELEC-007": "Circuit trip",
    "ELEC-011": "Lighting panel fault",
    "ELEC-015": "Generator warning alarm",
    "LIFT-002": "Door malfunction",
    "LIFT-005": "Cabin leveling fault",
    "LIFT-008": "Control panel reset",
    "FIRE-002": "Detector false alarm",
    "FIRE-006": "Suppression valve issue",
    "BMS-003": "Sensor communication fault",
    "BMS-009": "Setpoint drift",
    "SEC-004": "Access reader failure",
    "SEC-008": "Camera offline",
    "WATR-002": "Pump cavitation",
    "WATR-006": "Low pressure alert",
    "STRC-001": "Door closer failure",
    "STRC-004": "Ceiling tile leak stain",
    "ROOF-003": "Roof drain blockage",
    "IT-002": "Network cabinet overheat",
    "IT-005": "UPS battery alert",
    "GEN-001": "General handyman request",
    "GEN-005": "Furniture repair",
    "LAND-002": "Landscape irrigation issue",
    "PARK-004": "Barrier gate fault",
    "CUST-001": "Tenant comfort complaint",
}

CITY_CATALOG = [
    ("Mumbai", "West", "Commercial Tower"),
    ("Bengaluru", "South", "Tech Park"),
    ("Hyderabad", "South", "Life Sciences Campus"),
    ("Pune", "West", "Business Park"),
    ("Chennai", "South", "Corporate Office"),
    ("Delhi", "North", "Mixed Use Campus"),
    ("Gurugram", "North", "Grade A Office"),
    ("Noida", "North", "Command Center"),
    ("Kolkata", "East", "Operations Hub"),
    ("Ahmedabad", "West", "Industrial Campus"),
]
MANUFACTURERS = ["Daikin", "Carrier", "Johnson Controls", "Schneider Electric", "Otis", "Grundfos", "Honeywell", "Siemens"]
FIRST_NAMES = ["Aarav", "Vivaan", "Arjun", "Ishaan", "Aditya", "Neha", "Priya", "Anika", "Rohan", "Kiran", "Meera", "Kabir"]
LAST_NAMES = ["Sharma", "Patel", "Reddy", "Iyer", "Nair", "Gupta", "Kapoor", "Rao", "Mehta", "Menon"]


def build_patterns() -> list[RecurringPattern]:
    base_date = datetime(2024, 1, 15)
    patterns: list[RecurringPattern] = []
    skill_prefixes = ["HV", "PL", "EL", "LF", "BM"]
    codes = list(PROBLEM_CODES.items())[:15]
    for index, (problem_code, description) in enumerate(codes, start=1):
        interval = [47, 30, 21, 60, 75, 14, 28, 35, 90, 45, 32, 62, 50, 26, 55][index - 1]
        patterns.append(
            RecurringPattern(
                asset_id=f"ASSET-{index:03d}",
                location_id=f"LOC-{((index - 1) % 50) + 1:02d}",
                problem_code=problem_code,
                problem_description=description,
                interval_days=interval,
                occurrences=12 if interval <= 35 else 8,
                start_date=base_date + timedelta(days=index * 3),
                asset_category=["HVAC", "Plumbing", "Electrical", "Lift", "BMS"][index % 5],
                asset_age_category=["old", "mid", "new"][index % 3],
                technician_prefix=skill_prefixes[index % len(skill_prefixes)],
                base_cost=350 + index * 45,
            )
        )
    return patterns


def season_from_month(month: int) -> str:
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "fall"


def build_records() -> pd.DataFrame:
    random.seed(RANDOM_SEED)

    records: list[dict] = []
    work_order_counter = 1
    patterns = build_patterns()

    for pattern in patterns:
        for occurrence in range(pattern.occurrences):
            created_date = pattern.start_date + timedelta(days=pattern.interval_days * occurrence)
            created_date += timedelta(days=random.randint(-2, 2))
            resolution_hours = round(max(1.0, RNG.normal(2.5, 0.6)), 2)
            closed_date = created_date + timedelta(hours=resolution_hours)
            records.append(
                {
                    "work_order_id": f"WO-{work_order_counter:05d}",
                    "asset_id": pattern.asset_id,
                    "location_id": pattern.location_id,
                    "problem_code": pattern.problem_code,
                    "problem_description": pattern.problem_description,
                    "created_date": created_date,
                    "closed_date": closed_date,
                    "technician_id": f"{pattern.technician_prefix}-{random.randint(100, 999)}",
                    "priority": random.choice(["High", "High", "Medium"]),
                    "cost": round(pattern.base_cost + RNG.normal(0, 45), 2),
                    "resolution_code": random.choice(["RESET", "CLEANED", "REPLACED", "INSPECTED"]),
                    "asset_category": pattern.asset_category,
                    "asset_age_category": pattern.asset_age_category,
                    "resolution_hours": resolution_hours,
                    "season_flag": season_from_month(created_date.month),
                }
            )
            work_order_counter += 1

    asset_ids = [f"ASSET-{index:03d}" for index in range(1, 501)]
    location_ids = [f"LOC-{index:02d}" for index in range(1, 51)]
    categories = ["HVAC", "Plumbing", "Electrical", "Lift", "BMS", "Fire", "Security", "General"]
    problem_items = list(PROBLEM_CODES.items())
    start_window = datetime(2024, 1, 1)
    end_window = datetime(2025, 12, 31)
    total_days = (end_window - start_window).days

    while len(records) < 5000:
        created_date = start_window + timedelta(days=random.randint(0, total_days), hours=random.randint(0, 23))
        problem_code, description = random.choice(problem_items)
        resolution_hours = round(max(0.5, RNG.normal(3.2, 1.3)), 2)
        closed_date = created_date + timedelta(hours=resolution_hours)
        category = random.choice(categories)
        technician_prefix = {"HVAC": "HV", "Plumbing": "PL", "Electrical": "EL", "Lift": "LF", "BMS": "BM", "Fire": "FR", "Security": "SC", "General": "GN"}[category]
        work_order = {
            "work_order_id": f"WO-{work_order_counter:05d}",
            "asset_id": random.choice(asset_ids),
            "location_id": random.choice(location_ids),
            "problem_code": problem_code,
            "problem_description": description,
            "created_date": created_date,
            "closed_date": closed_date,
            "technician_id": f"{technician_prefix}-{random.randint(100, 999)}",
            "priority": random.choice(["Low", "Medium", "High", "Critical"]),
            "cost": round(max(85.0, RNG.normal(420, 160)), 2),
            "resolution_code": random.choice(["RESET", "REPLACED", "PATCHED", "INSPECTED", None]),
            "asset_category": category,
            "asset_age_category": random.choice(["new", "mid", "old"]),
            "resolution_hours": resolution_hours,
            "season_flag": season_from_month(created_date.month),
        }
        if random.random() < 0.03:
            work_order["technician_id"] = None
        if random.random() < 0.02:
            work_order["resolution_code"] = None
        records.append(work_order)
        if random.random() < 0.01:
            duplicate = work_order.copy()
            duplicate["work_order_id"] = f"WO-{work_order_counter + 1:05d}"
            records.append(duplicate)
            work_order_counter += 1
        work_order_counter += 1

    dataframe = pd.DataFrame(records).sort_values("created_date").reset_index(drop=True)
    return dataframe.iloc[:5000].copy()


def build_facility_seed(dataframe: pd.DataFrame) -> pd.DataFrame:
    facilities: list[dict] = []
    for index, location_id in enumerate(sorted(dataframe["location_id"].dropna().unique()), start=1):
        city, region, property_type = CITY_CATALOG[(index - 1) % len(CITY_CATALOG)]
        facilities.append(
            {
                "location_id": location_id,
                "facility_name": f"{city} Smart Facility {index:02d}",
                "city": city,
                "region": region,
                "country": "India",
                "property_type": property_type,
                "gross_area_sqft": int(120000 + (index * 8500)),
                "criticality_tier": ["Tier 1", "Tier 2", "Tier 3"][index % 3],
                "occupancy_band": ["High", "Medium", "High", "Low"][index % 4],
            }
        )
    return pd.DataFrame(facilities)


def build_asset_seed(dataframe: pd.DataFrame) -> pd.DataFrame:
    asset_groups = dataframe.groupby("asset_id", as_index=False).agg(
        location_id=("location_id", "first"),
        asset_category=("asset_category", lambda values: values.mode().iloc[0] if not values.mode().empty else "General"),
    )
    assets: list[dict] = []
    for index, row in enumerate(asset_groups.to_dict(orient="records"), start=1):
        category = row["asset_category"] or "General"
        install_date = datetime(2014, 1, 1) + timedelta(days=index * 23)
        assets.append(
            {
                "asset_id": row["asset_id"],
                "location_id": row["location_id"],
                "asset_name": f"{category} Asset {index:03d}",
                "asset_category": category,
                "manufacturer": MANUFACTURERS[index % len(MANUFACTURERS)],
                "model_number": f"{category[:3].upper()}-{1000 + index}",
                "install_date": install_date.date().isoformat(),
                "health_index": round(max(58.0, min(98.0, 92 - (index % 37) * 0.8)), 2),
                "service_level": ["24x7", "Business Hours", "Critical Response"][index % 3],
                "criticality_rank": ["High", "Medium", "Critical", "Medium"][index % 4],
            }
        )
    return pd.DataFrame(assets)


def build_technician_seed(dataframe: pd.DataFrame) -> pd.DataFrame:
    technician_ids = sorted(value for value in dataframe["technician_id"].dropna().unique() if value)
    technicians: list[dict] = []
    for index, technician_id in enumerate(technician_ids, start=1):
        first_name = FIRST_NAMES[index % len(FIRST_NAMES)]
        last_name = LAST_NAMES[index % len(LAST_NAMES)]
        technicians.append(
            {
                "technician_id": technician_id,
                "technician_name": f"{first_name} {last_name}",
                "primary_skill": {
                    "HV": "HVAC Specialist",
                    "PL": "Plumbing Specialist",
                    "EL": "Electrical Specialist",
                    "LF": "Lift Technician",
                    "BM": "BMS Specialist",
                    "FR": "Fire Systems Technician",
                    "SC": "Security Systems Technician",
                    "GN": "General Technician",
                }.get(str(technician_id).split("-", 1)[0], "General Technician"),
                "region": CITY_CATALOG[index % len(CITY_CATALOG)][1],
                "shift": ["Day", "Evening", "Night"][index % 3],
            }
        )
    return pd.DataFrame(technicians)


def export_artifacts(dataframe: pd.DataFrame) -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(CSV_PATH, index=False)
    facilities = build_facility_seed(dataframe)
    assets = build_asset_seed(dataframe)
    technicians = build_technician_seed(dataframe)
    with sqlite3.connect(DB_PATH) as connection:
        dataframe.to_sql("work_orders_seed", connection, if_exists="replace", index=False)
        facilities.to_sql("facilities_seed", connection, if_exists="replace", index=False)
        assets.to_sql("assets_seed", connection, if_exists="replace", index=False)
        technicians.to_sql("technicians_seed", connection, if_exists="replace", index=False)
    SCHEMA_PATH.write_text(
        """
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
        """.strip() + "\n",
        encoding="utf-8",
    )


def main() -> None:
    dataframe = build_records()
    export_artifacts(dataframe)
    print(f"Generated {len(dataframe)} work orders at {CSV_PATH}")
    print(f"SQLite seed written to {DB_PATH}")


if __name__ == "__main__":
    main()
