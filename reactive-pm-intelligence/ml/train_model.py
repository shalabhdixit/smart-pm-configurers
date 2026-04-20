from backend.models.database import init_db, session_scope
from backend.services.pattern_engine import build_work_order_dataframe, detect_recurring_patterns, persist_patterns
from backend.services.prediction_engine import predict_patterns


def main() -> None:
    init_db()
    with session_scope() as session:
        dataframe = build_work_order_dataframe(session)
        patterns = detect_recurring_patterns(dataframe)
        persist_patterns(session, patterns)
        predictions = predict_patterns(session)
        print(f"Trained model and generated {len(predictions)} predictions")


if __name__ == "__main__":
    main()