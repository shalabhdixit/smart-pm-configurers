from backend.models.database import init_db, session_scope
from backend.services.ingestion_service import ingest_work_orders, load_dataframe
from backend.services.pattern_engine import build_work_order_dataframe, detect_recurring_patterns, persist_patterns
from backend.services.prediction_engine import predict_patterns


def test_prediction_engine_persists_probability_records():
    init_db()
    dataframe = load_dataframe("data/sample_work_orders.csv")
    with session_scope() as session:
        ingest_work_orders(session, dataframe)
        work_orders = build_work_order_dataframe(session)
        patterns = detect_recurring_patterns(work_orders)
        persist_patterns(session, patterns)
        predictions = predict_patterns(session)
    assert predictions
    assert 0 <= predictions[0].recurrence_probability_90d <= 1
    assert "risk_score" in predictions[0].explanation