# ML Model Card

## 1. Model Purpose

The recurrence model predicts how likely a detected pattern is to recur within the next 30, 60, and 90 days. Its operational purpose is not academic forecasting alone; it exists to trigger preventive maintenance decisions early enough to avoid repeat breakdowns.

## 2. Decision Supported

Primary decision:

- should this recurring pattern be converted into planned maintenance now

Secondary decisions:

- how urgently the PM should be scheduled
- which assets and facilities deserve executive focus
- which patterns belong in the assistant narrative and dashboard prioritization

## 3. Training Data

Current training corpus:

- synthetic CAFM-like work-order history
- approximately 5,000 work orders
- 500 assets
- 50 facilities
- embedded repeat-failure signatures for demo realism

## 4. Unit Of Prediction

The model scores the `PatternRecord` entity, not the raw work order.

This is deliberate because PM conversion decisions are made against recurring signatures, not single tickets.

## 5. Input Features

Numerical:

- `occurrence_count`
- `avg_interval_days`
- `std_interval_days`
- `coefficient_of_variation`
- `days_since_last_occurrence`
- `avg_resolution_hours`
- `avg_cost`

Categorical:

- `asset_age_category`
- `season_mode`
- `priority_mode`

## 6. Label Strategy

The current label is deterministic and heuristic:

- positive when a pattern has interval less than or equal to 90 days and occurrence count of at least 4

Why this was chosen:

- enables end-to-end modeling before real labeled PM avoidance outcomes exist

Trade-off:

- useful for a pilot demonstration, but not yet a production-quality supervisory target

## 7. Model Type

- algorithm: Random Forest classifier
- preprocessing: median imputation for numeric features and one-hot encoding for categorical features
- validation: K-fold cross-validation with predicted probabilities used for AUC calculation

## 8. Outputs

For each pattern the system stores:

- 30 day recurrence probability
- 60 day recurrence probability
- 90 day recurrence probability
- lower confidence bound
- upper confidence bound
- explanation payload with lightweight feature contribution signals

## 9. Explainability Approach

The model currently exposes grouped feature importance contributions rather than local explanation packages such as SHAP.

Why this is acceptable for the pilot:

- lightweight
- deterministic
- easy to expose in APIs and UI

What should improve in production:

- persistent model versioning
- richer per-prediction explanation artifacts
- monitored drift and feature attribution governance

## 10. Performance View

The pipeline stores AUC-ROC in the explanation payload for scored predictions. This is enough for demo calibration and smoke validation, but not sufficient for enterprise governance.

Production metrics to add:

- precision at PM conversion threshold
- recall for repeat-failure capture
- false positive rate by asset class
- calibration drift over time

## 11. Risks And Limitations

- synthetic data does not capture all operational behaviors seen in live portfolios
- labels are heuristic rather than outcome-derived
- current feature set does not yet include IoT or BMS telemetry
- model is retrained in-process rather than through a governed ML pipeline

## 12. Safety And Bias Considerations

- no PII is used in the model
- workforce-related fields are not used as human ranking attributes
- bias monitoring should still evaluate skew by geography, client type, and asset category in production

## 13. Productionization Recommendations

- replace heuristic labels with observed recurrence and PM outcome labels
- version datasets, features, and model artifacts
- add offline evaluation datasets from real accounts
- move retraining to a governed scheduled workflow
- add approval thresholds before auto-publishing PMs downstream

## 14. Retraining

Current process:

```powershell
python ml/train_model.py
```

Recommended production process:

- scheduled training job
- validation gate
- model registry publication
- controlled rollout with rollback path