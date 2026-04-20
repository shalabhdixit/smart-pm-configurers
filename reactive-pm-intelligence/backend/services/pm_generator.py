from __future__ import annotations

from datetime import timedelta

from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.models.database import PMSchedule, PatternRecord, PredictionRecord
from backend.utils.helpers import frequency_from_interval


settings = get_settings()


def generate_pm_schedule(pattern: PatternRecord) -> dict:
    """Generate a PM schedule payload from a recurring pattern."""

    next_due_date = pattern.last_occurrence_date + timedelta(days=max(1, round(pattern.avg_interval_days * 0.85)))
    return {
        "pattern_key": pattern.pattern_key,
        "pm_title": f"Preventive: {pattern.problem_code} for Asset {pattern.asset_id}",
        "frequency": frequency_from_interval(pattern.avg_interval_days),
        "next_due_date": next_due_date,
        "priority": pattern.priority_mode,
        "estimated_duration": round(pattern.avg_resolution_hours, 2),
        "assigned_skill_set": pattern.assigned_skill_set,
        "source_payload": {
            "asset_id": pattern.asset_id,
            "location_id": pattern.location_id,
            "problem_code": pattern.problem_code,
            "regularity_score": pattern.regularity_score,
            "avg_interval_days": pattern.avg_interval_days,
        },
    }


def generate_pm_schedules(session: Session) -> list[PMSchedule]:
    """Create PM schedules for predictions above the configured threshold."""

    session.query(PMSchedule).delete()
    predictions = session.query(PredictionRecord).all()
    if not predictions:
        return []
    pattern_map = {pattern.pattern_key: pattern for pattern in session.query(PatternRecord).all()}
    schedules: list[PMSchedule] = []
    for prediction in predictions:
        if prediction.recurrence_probability_90d < settings.pm_probability_threshold:
            continue
        pattern = pattern_map.get(prediction.pattern_key)
        if not pattern:
            continue
        payload = generate_pm_schedule(pattern)
        schedule = PMSchedule(**payload)
        session.add(schedule)
        schedules.append(schedule)
    session.flush()
    return schedules