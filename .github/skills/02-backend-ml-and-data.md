# Skill 02: Backend, ML, And Data

Use this skill when building the synthetic dataset, backend services, machine learning logic, and API surface.

## Synthetic Data Requirements

Create two years of realistic synthetic work orders with:

- 500 unique assets.
- 50 locations.
- 30 problem codes across HVAC, plumbing, electrical, elevators, and similar building systems.
- About 5,000 total work orders.
- 15 deliberate recurring patterns.
- Seasonal and periodic behavior.
- One-off incidents and mild data quality noise.
- Cost, technician, and resolution detail.

The generated sample data must be good enough that the recurring-pattern engine can reliably detect the embedded patterns.

## Backend Modules Required

Create at least the following modules:

- `backend/models/database.py`
- `backend/models/schemas.py`
- `backend/services/ingestion_service.py`
- `backend/services/pattern_engine.py`
- `backend/services/prediction_engine.py`
- `backend/services/pm_generator.py`
- `backend/api/routes.py`
- `backend/main.py`
- `backend/config.py`
- `backend/scheduler.py`
- `backend/utils/logger.py`
- `backend/utils/helpers.py`

## Pattern Detection Requirements

Group work orders by `(asset_id, location_id, problem_code)`.

For each group, compute:

- occurrence count
- average interval in days
- interval standard deviation
- coefficient of variation
- last occurrence date
- days since last occurrence
- regularity score

Flag a pattern as recurring when the occurrence count and interval thresholds indicate repeated behavior. Keep the thresholds configurable.

Prefer outputs that can directly power the dashboard and PM generator.

## Prediction Engine Requirements

Use a model that predicts recurrence within future windows, ideally 30, 60, and 90 days.

Feature candidates include:

- `occurrence_count`
- `avg_interval_days`
- `std_interval_days`
- `coefficient_of_variation`
- `days_since_last_occurrence`
- `asset_age_category`
- `season_mode`
- `avg_resolution_hours`
- `avg_cost`
- `priority_mode_encoded`

Preferred implementation path:

- Train a `RandomForestClassifier`.
- Use 5-fold cross-validation.
- Report AUC-ROC.
- Save the trained model artifact.
- Produce explainability output for the top features influencing each prediction.

If survival analysis is included, treat it as an enhancement rather than a blocker.

## PM Generator Requirements

Generate schedules only for patterns above the configured recurrence threshold.

Every PM schedule should contain:

- a strong PM title
- frequency bucket
- next due date
- priority
- estimated duration
- assigned skill set
- source pattern metadata

Use historical interval logic with an 85% proactive buffer for next due date calculation.

## API Requirements

Implement these endpoints:

- `POST /api/v1/ingest`
- `GET /api/v1/patterns`
- `GET /api/v1/patterns/{id}`
- `GET /api/v1/predictions`
- `POST /api/v1/pm/generate`
- `GET /api/v1/pm/schedules`
- `GET /api/v1/dashboard/kpis`
- `GET /api/v1/health`

Also include:

- Pydantic models for requests and responses.
- Simulated JWT auth.
- Rate limiting.
- CORS.
- Health checks.
- OpenAPI docs.
- Structured logging.

## Reliability And Observability

Implement or document:

- JSON logging.
- health endpoint dependency checks.
- `/metrics` for Prometheus if feasible.
- scheduler execution logging.
- graceful shutdown behavior.
- retry logic for external integration stubs.

## Testing Focus

Add tests for:

- recurring-pattern detection
- recurrence prediction output contracts
- PM schedule generation logic
- API route happy paths and basic edge cases