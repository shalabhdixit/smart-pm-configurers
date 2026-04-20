from __future__ import annotations

import pickle
from pathlib import Path
from tempfile import mkdtemp

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.models.database import PatternRecord, PredictionRecord


settings = get_settings()

FEATURE_COLUMNS = [
    "occurrence_count",
    "avg_interval_days",
    "std_interval_days",
    "coefficient_of_variation",
    "days_since_last_occurrence",
    "asset_age_category",
    "season_mode",
    "avg_resolution_hours",
    "avg_cost",
    "priority_mode",
]


def build_training_frame(patterns: list[PatternRecord]) -> pd.DataFrame:
    """Create a training frame using pattern records and a deterministic label."""

    rows = []
    for pattern in patterns:
        label = 1 if pattern.avg_interval_days <= 90 and pattern.occurrence_count >= 4 else 0
        rows.append(
            {
                "pattern_key": pattern.pattern_key,
                "occurrence_count": pattern.occurrence_count,
                "avg_interval_days": pattern.avg_interval_days,
                "std_interval_days": pattern.std_interval_days,
                "coefficient_of_variation": pattern.coefficient_of_variation,
                "days_since_last_occurrence": max(0, (pd.Timestamp.utcnow().date() - pattern.last_occurrence_date).days),
                "asset_age_category": pattern.asset_age_category,
                "season_mode": pattern.season_mode,
                "avg_resolution_hours": pattern.avg_resolution_hours,
                "avg_cost": pattern.avg_cost,
                "priority_mode": pattern.priority_mode,
                "label": label,
            }
        )
    return pd.DataFrame(rows)


def train_prediction_model(frame: pd.DataFrame) -> tuple[Pipeline, float]:
    """Train a recurrence classifier and return the fitted model and AUC."""

    categorical = ["asset_age_category", "season_mode", "priority_mode"]
    numeric = [column for column in FEATURE_COLUMNS if column not in categorical]
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric),
            (
                "categorical",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("encoder", OneHotEncoder(handle_unknown="ignore")),
                ]),
                categorical,
            ),
        ]
    )
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=250,
                    random_state=settings.random_seed,
                    class_weight="balanced",
                    min_samples_leaf=2,
                    max_features="sqrt",
                ),
            ),
        ],
        memory=mkdtemp(prefix="reactive-pm-pipeline-"),
    )
    X = frame[FEATURE_COLUMNS]
    y = frame["label"]
    if y.nunique() == 1:
        y = pd.Series(np.where(frame["avg_interval_days"] <= 90, 1, 0))
    cv = KFold(n_splits=min(5, len(frame)), shuffle=True, random_state=settings.random_seed)
    scores = cross_val_predict(model, X, y, cv=cv, method="predict_proba")[:, 1]
    auc = roc_auc_score(y, scores) if y.nunique() > 1 else 1.0
    model.fit(X, y)
    settings.model_path.parent.mkdir(parents=True, exist_ok=True)
    with settings.model_path.open("wb") as file_obj:
        pickle.dump(model, file_obj)
    return model, float(auc)


def predict_patterns(session: Session) -> list[PredictionRecord]:
    """Train a model from pattern data and persist predictions."""

    patterns = session.query(PatternRecord).all()
    if not patterns:
        return []
    frame = build_training_frame(patterns)
    model, auc = train_prediction_model(frame)
    probabilities = model.predict_proba(frame[FEATURE_COLUMNS])[:, 1]
    session.query(PredictionRecord).delete()
    prediction_records: list[PredictionRecord] = []
    classifier = model.named_steps["classifier"]
    feature_importance = _extract_feature_importance(model, classifier)
    for row, probability in zip(frame.to_dict(orient="records"), probabilities, strict=False):
        explanation = _explain_prediction(row, probability, feature_importance)
        prediction = PredictionRecord(
            pattern_key=row["pattern_key"],
            recurrence_probability_30d=round(min(0.99, probability * 0.9), 4),
            recurrence_probability_60d=round(min(0.99, probability * 0.97), 4),
            recurrence_probability_90d=round(min(0.99, probability), 4),
            confidence_low=round(max(0.0, probability - 0.08), 4),
            confidence_high=round(min(0.99, probability + 0.08), 4),
            explanation={**explanation, "model_auc_roc": round(auc, 4)},
        )
        session.add(prediction)
        prediction_records.append(prediction)
    session.flush()
    return prediction_records


def _extract_feature_importance(model: Pipeline, classifier: RandomForestClassifier) -> dict[str, float]:
    names = model.named_steps["preprocessor"].get_feature_names_out().tolist()
    weights = classifier.feature_importances_.tolist()
    grouped: dict[str, float] = {}
    for name, weight in zip(names, weights, strict=False):
        if "__" in name:
            _, feature_name = name.split("__", 1)
        else:
            feature_name = name
        grouped[feature_name] = grouped.get(feature_name, 0.0) + float(weight)
    return grouped


def _explain_prediction(row: dict, probability: float, feature_importance: dict[str, float]) -> dict[str, float]:
    explanation: dict[str, float] = {}
    for feature_name in ("avg_interval_days", "occurrence_count", "coefficient_of_variation", "avg_cost", "avg_resolution_hours"):
        importance = feature_importance.get(feature_name, 0.0)
        value = float(row.get(feature_name, 0.0))
        explanation[feature_name] = round(importance * max(value, 1.0), 4)
    explanation["risk_score"] = round(probability, 4)
    return explanation


def load_model(path: Path | None = None) -> Pipeline:
    """Load the saved model artifact from disk."""

    model_path = path or settings.model_path
    with model_path.open("rb") as file_obj:
        return pickle.load(file_obj)