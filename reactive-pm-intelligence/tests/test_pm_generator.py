from backend.models.database import init_db, session_scope
from backend.services.ingestion_service import ingest_work_orders, load_dataframe
from backend.services.pattern_engine import build_work_order_dataframe, detect_recurring_patterns, persist_patterns
from backend.services.pm_generator import generate_pm_schedules
from backend.services.prediction_engine import predict_patterns


def test_pm_generator_creates_schedules_for_high_risk_patterns():
    init_db()
    dataframe = load_dataframe("data/sample_work_orders.csv")
    with session_scope() as session:
        ingest_work_orders(session, dataframe)
        work_orders = build_work_order_dataframe(session)
        patterns = detect_recurring_patterns(work_orders)
        persist_patterns(session, patterns)
        predict_patterns(session)
        schedules = generate_pm_schedules(session)
    assert schedules
    assert schedules[0].frequency in {"Weekly", "Monthly", "Quarterly", "Semi-Annual", "Annual"}