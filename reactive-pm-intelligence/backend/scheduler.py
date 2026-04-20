from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from backend.models.database import session_scope, truncate_analytics
from backend.services.pattern_engine import build_work_order_dataframe, detect_recurring_patterns, persist_patterns
from backend.services.pm_generator import generate_pm_schedules
from backend.services.prediction_engine import predict_patterns
from backend.utils.logger import get_logger


logger = get_logger(__name__)


def run_daily_pipeline() -> dict[str, int]:
    """Run the analytics pipeline from source work orders to PM schedules."""

    with session_scope() as session:
        truncate_analytics(session)
        work_orders = build_work_order_dataframe(session)
        patterns_df = detect_recurring_patterns(work_orders)
        persist_patterns(session, patterns_df)
        predictions = predict_patterns(session)
        schedules = generate_pm_schedules(session)
        summary = {
            "patterns": len(patterns_df),
            "predictions": len(predictions),
            "schedules": len(schedules),
        }
        logger.info("Pipeline completed", extra=summary)
        return summary


def create_scheduler() -> BackgroundScheduler:
    """Create the APScheduler instance used by the app."""

    scheduler = BackgroundScheduler()
    scheduler.add_job(run_daily_pipeline, "interval", days=1, id="daily-reactive-pm-pipeline", replace_existing=True)
    return scheduler