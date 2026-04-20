from backend.models.database import SessionLocal
from backend.services.prediction_engine import load_model


def main() -> None:
    model = load_model()
    print(f"Loaded model pipeline: {model}")
    with SessionLocal() as session:
        predictions = session.execute("SELECT COUNT(*) FROM predictions").scalar_one_or_none()
        print(f"Persisted predictions: {predictions}")


if __name__ == "__main__":
    main()