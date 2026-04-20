from backend.models.database import init_db, session_scope
from backend.services.ingestion_service import ingest_work_orders, load_dataframe
from backend.services.pattern_engine import build_work_order_dataframe, detect_recurring_patterns


def test_detect_recurring_patterns_returns_expected_signature_rows():
    init_db()
    dataframe = load_dataframe("data/sample_work_orders.csv")
    with session_scope() as session:
        ingest_work_orders(session, dataframe.head(500))
        work_orders = build_work_order_dataframe(session)
        patterns = detect_recurring_patterns(work_orders)
    assert not patterns.empty
    assert {"pattern_key", "regularity_score", "occurrence_count"}.issubset(patterns.columns)
    assert patterns.iloc[0]["regularity_score"] >= 0