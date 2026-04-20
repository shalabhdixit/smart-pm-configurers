from __future__ import annotations

from math import log

import pandas as pd
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.models.database import PatternRecord, WorkOrder
from backend.utils.helpers import coefficient_of_variation, mode_or_default


settings = get_settings()
DEFAULT_SKILL_SET = "General Technician"


def build_work_order_dataframe(session: Session) -> pd.DataFrame:
    """Load work orders from the database into a pandas DataFrame."""

    rows = session.query(WorkOrder).all()
    data = [
        {
            "work_order_id": row.work_order_id,
            "asset_id": row.asset_id,
            "location_id": row.location_id,
            "problem_code": row.problem_code,
            "problem_description": row.problem_description,
            "created_date": row.created_date,
            "closed_date": row.closed_date,
            "technician_id": row.technician_id,
            "priority": row.priority,
            "cost": row.cost,
            "resolution_code": row.resolution_code,
            "asset_category": row.asset_category,
            "asset_age_category": row.asset_age_category,
            "resolution_hours": row.resolution_hours,
            "season_flag": row.season_flag,
        }
        for row in rows
    ]
    return pd.DataFrame(data)


def detect_recurring_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """Detect recurring work-order patterns using grouped interval statistics."""

    if df.empty:
        return pd.DataFrame()

    working_df = df.copy().sort_values("created_date")
    results: list[dict] = []
    for (asset_id, location_id, problem_code), group in working_df.groupby(["asset_id", "location_id", "problem_code"]):
        group = group.sort_values("created_date")
        occurrence_count = int(len(group))
        intervals = group["created_date"].diff().dt.days.dropna()
        avg_interval = float(intervals.mean()) if not intervals.empty else 999.0
        std_interval = float(intervals.std(ddof=0)) if not intervals.empty else 0.0
        cv = coefficient_of_variation(intervals) if not intervals.empty else 0.0
        regularity_score = max(0.0, (1 - cv)) * log(max(occurrence_count, 1))
        is_recurring = occurrence_count >= settings.recurring_min_occurrences and avg_interval <= settings.recurring_max_interval_days
        if not is_recurring:
            continue
        results.append(
            {
                "pattern_key": f"{asset_id}|{location_id}|{problem_code}",
                "asset_id": asset_id,
                "location_id": location_id,
                "problem_code": problem_code,
                "occurrence_count": occurrence_count,
                "avg_interval_days": round(avg_interval, 2),
                "std_interval_days": round(std_interval, 2),
                "coefficient_of_variation": round(cv, 4),
                "regularity_score": round(regularity_score, 4),
                "last_occurrence_date": group["created_date"].max().date(),
                "days_since_last_occurrence": int((pd.Timestamp.utcnow().tz_localize(None) - group["created_date"].max()).days),
                "avg_resolution_hours": round(float(group["resolution_hours"].mean()), 2),
                "avg_cost": round(float(group["cost"].mean()), 2),
                "priority_mode": mode_or_default(group["priority"], "Medium"),
                "asset_category": mode_or_default(group["asset_category"], "General"),
                "asset_age_category": mode_or_default(group["asset_age_category"], "mid"),
                "season_mode": mode_or_default(group["season_flag"], "summer"),
                "assigned_skill_set": mode_or_default(group["technician_id"].fillna(DEFAULT_SKILL_SET).map(_technician_to_skill), DEFAULT_SKILL_SET),
                "timeline": [value.isoformat() for value in group["created_date"]],
            }
        )

    result_df = pd.DataFrame(results)
    if result_df.empty:
        return result_df

    forest = IsolationForest(random_state=settings.random_seed, contamination=0.1)
    result_df["anomaly_flag"] = forest.fit_predict(result_df[["occurrence_count", "avg_interval_days", "regularity_score"]])
    return result_df.sort_values("regularity_score", ascending=False).reset_index(drop=True)


def _technician_to_skill(technician_id: str) -> str:
    if technician_id.startswith("HV"):
        return "HVAC Specialist"
    if technician_id.startswith("PL"):
        return "Plumbing Specialist"
    if technician_id.startswith("EL"):
        return "Electrical Specialist"
    if technician_id.startswith("LF"):
        return "Lift Technician"
    return DEFAULT_SKILL_SET


def persist_patterns(session: Session, patterns_df: pd.DataFrame) -> list[PatternRecord]:
    """Store detected patterns in the database."""

    session.query(PatternRecord).delete()
    pattern_records: list[PatternRecord] = []
    for row in patterns_df.to_dict(orient="records"):
        pattern = PatternRecord(**{key: value for key, value in row.items() if key in PatternRecord.__table__.columns.keys()})
        session.add(pattern)
        pattern_records.append(pattern)
    session.flush()
    return pattern_records