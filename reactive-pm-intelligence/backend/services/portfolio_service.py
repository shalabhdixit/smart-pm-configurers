from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.models.database import Asset, Facility, PMSchedule, PatternRecord, PredictionRecord, Technician, WorkOrder


settings = get_settings()

CITY_CATALOG = [
    ("Mumbai", "West", "Commercial Tower"),
    ("Bengaluru", "South", "Tech Park"),
    ("Hyderabad", "South", "Life Sciences Campus"),
    ("Pune", "West", "Business Park"),
    ("Chennai", "South", "Corporate Office"),
    ("Delhi", "North", "Mixed Use Campus"),
    ("Gurugram", "North", "Grade A Office"),
    ("Noida", "North", "Command Center"),
]
MANUFACTURERS = ["Daikin", "Carrier", "Johnson Controls", "Schneider Electric", "Otis", "Grundfos", "Honeywell", "Siemens"]
FIRST_NAMES = ["Aarav", "Vivaan", "Arjun", "Ishaan", "Aditya", "Neha", "Priya", "Anika", "Rohan", "Kiran", "Meera", "Kabir"]
LAST_NAMES = ["Sharma", "Patel", "Reddy", "Iyer", "Nair", "Gupta", "Kapoor", "Rao", "Mehta", "Menon"]


def sync_reference_entities(session: Session) -> None:
    """Populate facility, asset, and technician reference tables from ingested work orders."""

    work_orders = session.scalars(select(WorkOrder)).all()
    if not work_orders:
        return

    _seed_facilities(session, work_orders)
    _seed_assets(session, work_orders)
    _seed_technicians(session, work_orders)
    session.flush()


def build_portfolio_overview(session: Session) -> dict:
    """Build an executive-friendly portfolio snapshot for UI and assistant use."""

    facilities = {item.location_id: item for item in session.scalars(select(Facility)).all()}
    assets = {item.asset_id: item for item in session.scalars(select(Asset)).all()}
    work_orders = session.scalars(select(WorkOrder)).all()
    patterns = session.scalars(select(PatternRecord)).all()
    predictions = session.scalars(select(PredictionRecord)).all()
    schedules = session.scalars(select(PMSchedule)).all()

    work_order_counts = _count_work_orders_by_location(work_orders)
    facility_risk_counts = _count_risky_patterns_by_location(patterns, predictions)
    pm_candidates = _count_pm_candidates_by_location(schedules)
    top_facilities = _build_top_facilities(facilities, work_order_counts, facility_risk_counts, pm_candidates)
    at_risk_assets = _build_at_risk_assets(patterns, predictions, assets)

    return {
        "facilities": len(facilities),
        "assets": len(assets),
        "technicians": session.query(Technician).count(),
        "work_orders": len(work_orders),
        "top_facilities": top_facilities[: settings.assistant_top_facilities],
        "at_risk_assets": at_risk_assets[: settings.assistant_top_patterns],
    }


def _seed_facilities(session: Session, work_orders: list[WorkOrder]) -> None:
    existing = set(session.scalars(select(Facility.location_id)).all())
    location_ids = sorted({item.location_id for item in work_orders if item.location_id})
    for index, location_id in enumerate(location_ids, start=1):
        if location_id in existing:
            continue
        city, region, property_type = CITY_CATALOG[(index - 1) % len(CITY_CATALOG)]
        session.add(
            Facility(
                location_id=location_id,
                facility_name=f"{city} Smart Facility {index:02d}",
                city=city,
                region=region,
                country="India",
                property_type=property_type,
                gross_area_sqft=120000 + (index * 8500),
                criticality_tier=["Tier 1", "Tier 2", "Tier 3"][index % 3],
                occupancy_band=["High", "Medium", "High", "Low"][index % 4],
            )
        )


def _seed_assets(session: Session, work_orders: list[WorkOrder]) -> None:
    existing = set(session.scalars(select(Asset.asset_id)).all())
    grouped: dict[str, list[WorkOrder]] = defaultdict(list)
    for row in work_orders:
        grouped[row.asset_id].append(row)
    for index, (asset_id, rows) in enumerate(sorted(grouped.items()), start=1):
        if asset_id in existing:
            continue
        reference = rows[0]
        install_date = date(2014, 1, 1) + timedelta(days=index * 23)
        session.add(
            Asset(
                asset_id=asset_id,
                location_id=reference.location_id,
                asset_name=f"{reference.asset_category or 'General'} Asset {index:03d}",
                asset_category=reference.asset_category or "General",
                manufacturer=MANUFACTURERS[index % len(MANUFACTURERS)],
                model_number=f"{(reference.asset_category or 'GEN')[:3].upper()}-{1000 + index}",
                install_date=install_date,
                health_index=round(max(58.0, min(98.0, 92 - (index % 37) * 0.8)), 2),
                service_level=["24x7", "Business Hours", "Critical Response"][index % 3],
                criticality_rank=["High", "Medium", "Critical", "Medium"][index % 4],
            )
        )


def _seed_technicians(session: Session, work_orders: list[WorkOrder]) -> None:
    existing = set(session.scalars(select(Technician.technician_id)).all())
    technician_ids = sorted({item.technician_id for item in work_orders if item.technician_id})
    for index, technician_id in enumerate(technician_ids, start=1):
        if technician_id in existing:
            continue
        session.add(
            Technician(
                technician_id=technician_id,
                technician_name=f"{FIRST_NAMES[index % len(FIRST_NAMES)]} {LAST_NAMES[index % len(LAST_NAMES)]}",
                primary_skill=_skill_from_technician(technician_id),
                region=CITY_CATALOG[index % len(CITY_CATALOG)][1],
                shift=["Day", "Evening", "Night"][index % 3],
            )
        )


def _skill_from_technician(technician_id: str) -> str:
    prefix = str(technician_id).split("-", 1)[0]
    return {
        "HV": "HVAC Specialist",
        "PL": "Plumbing Specialist",
        "EL": "Electrical Specialist",
        "LF": "Lift Technician",
        "BM": "BMS Specialist",
        "FR": "Fire Systems Technician",
        "SC": "Security Systems Technician",
        "GN": "General Technician",
    }.get(prefix, "General Technician")


def _recommended_action(avg_interval_days: float, probability: float) -> str:
    if probability >= 0.9:
        return f"Trigger PM within {max(7, round(avg_interval_days * 0.6))} days"
    if probability >= 0.8:
        return f"Lock technician slot inside {max(10, round(avg_interval_days * 0.75))} days"
    return "Monitor and batch with next PM wave"


def _count_work_orders_by_location(work_orders: list[WorkOrder]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in work_orders:
        counts[row.location_id] += 1
    return counts


def _count_risky_patterns_by_location(patterns: list[PatternRecord], predictions: list[PredictionRecord]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    prediction_by_pattern = {item.pattern_key: item for item in predictions}
    for pattern in patterns:
        prediction = prediction_by_pattern.get(pattern.pattern_key)
        if prediction and prediction.recurrence_probability_90d >= settings.pm_probability_threshold:
            counts[pattern.location_id] += 1
    return counts


def _count_pm_candidates_by_location(schedules: list[PMSchedule]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for schedule in schedules:
        location_id = schedule.source_payload.get("location_id")
        if location_id:
            counts[location_id] += 1
    return counts


def _build_top_facilities(
    facilities: dict[str, Facility],
    work_order_counts: dict[str, int],
    facility_risk_counts: dict[str, int],
    pm_candidates: dict[str, int],
) -> list[dict]:
    facility_rows = [
        {
            "location_id": location_id,
            "facility_name": facility.facility_name,
            "city": facility.city,
            "property_type": facility.property_type,
            "reactive_work_orders": work_order_counts.get(location_id, 0),
            "high_risk_patterns": facility_risk_counts.get(location_id, 0),
            "open_pm_candidates": pm_candidates.get(location_id, 0),
        }
        for location_id, facility in facilities.items()
    ]
    facility_rows.sort(key=lambda item: (item["high_risk_patterns"], item["reactive_work_orders"]), reverse=True)
    return facility_rows[: settings.assistant_top_facilities]


def _build_at_risk_assets(patterns: list[PatternRecord], predictions: list[PredictionRecord], assets: dict[str, Asset]) -> list[dict]:
    at_risk_assets = []
    pattern_map = {item.pattern_key: item for item in patterns}
    prediction_rows = sorted(predictions, key=lambda item: item.recurrence_probability_90d, reverse=True)
    for prediction in prediction_rows[:8]:
        pattern = pattern_map.get(prediction.pattern_key)
        if not pattern:
            continue
        asset = assets.get(pattern.asset_id)
        at_risk_assets.append(
            {
                "asset_id": pattern.asset_id,
                "asset_name": asset.asset_name if asset else f"Asset {pattern.asset_id}",
                "location_id": pattern.location_id,
                "asset_category": pattern.asset_category,
                "health_index": asset.health_index if asset else round(max(55.0, 92 - prediction.recurrence_probability_90d * 35), 2),
                "recurrence_probability_90d": prediction.recurrence_probability_90d,
                "recommended_action": _recommended_action(pattern.avg_interval_days, prediction.recurrence_probability_90d),
            }
        )
    return at_risk_assets[: settings.assistant_top_patterns]
