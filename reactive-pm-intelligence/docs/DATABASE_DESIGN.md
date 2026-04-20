# Database Design

## 1. Database Objective

The current database design is optimized for pilot simplicity, deterministic demos, and explainable analytics generation. It uses SQLite with SQLAlchemy ORM models and is structured to support clean migration to PostgreSQL.

## 2. Physical Tables

### Reference Tables

- `facilities`
- `assets`
- `technicians`

### Operational Fact Table

- `work_orders`

### Derived Analytics Tables

- `patterns`
- `predictions`
- `pm_schedules`

### Seed Schema Artifacts

The SQL seed file in `data/schema.sql` defines:

- `work_orders_seed`
- `facilities_seed`
- `assets_seed`
- `technicians_seed`

These support documentation, demo generation, and external schema review.

## 3. Table-Level Design

### `work_orders`

Purpose:

- canonical source of reactive maintenance events

Key design choices:

- unique external work order identifier
- indexed `asset_id`, `location_id`, and `problem_code`
- timestamped `created_date` for interval analysis
- cost and duration retained for business value and explanation

### `patterns`

Purpose:

- materialized recurring signature table derived from `work_orders`

Key design choices:

- unique `pattern_key`
- persisted interval metrics for explainability and sorting
- JSON timeline for direct UI rendering

### `predictions`

Purpose:

- persisted model output for the current scoring pass

Key design choices:

- unique `pattern_key` for one-to-one alignment with pattern output
- 30, 60, and 90 day horizons for different operating cadences
- confidence bounds for executive communication
- explanation JSON for extensible interpretability

### `pm_schedules`

Purpose:

- generated preventive interventions ready for downstream integration

Key design choices:

- creation timestamp for auditability
- `source_payload` JSON so downstream systems preserve origin context

### `facilities`, `assets`, `technicians`

Purpose:

- provide the portfolio context needed for hotspot ranking, risk interpretation, and SLT communication

## 4. Indexing Strategy

Current indexes implied by ORM model definitions:

- unique indexes on `work_order_id`, `location_id`, `asset_id`, `technician_id`, and `pattern_key`
- secondary indexes on `asset_id`, `location_id`, `problem_code`, and several reference columns

Why this works for the pilot:

- most frequent filters are by asset, location, pattern key, and most recent created date
- current row volumes are modest and fit demo latency expectations

Recommended production indexes:

- composite index on `work_orders(asset_id, location_id, problem_code, created_date)`
- composite index on `patterns(location_id, regularity_score)`
- composite index on `predictions(recurrence_probability_90d desc)`
- index on `pm_schedules(next_due_date, priority)`

## 5. Rebuild Strategy For Derived Data

The platform intentionally treats `patterns`, `predictions`, and `pm_schedules` as rebuildable analytics state.

Pipeline rebuild sequence:

1. truncate analytics tables
2. detect patterns from `work_orders`
3. train and score predictions from `patterns`
4. generate PM schedules from `predictions`

Benefits:

- deterministic demo resets
- reduced complexity in reconciliation logic
- easier analytics iteration during pilot

Trade-off:

- not yet optimized for incremental high-frequency enterprise scoring

## 6. Data Retention View

### Retain Long-Term

- work orders
- facility, asset, and technician master context

### Rebuild On Demand

- patterns
- predictions
- PM schedules

Recommended enterprise enhancement:

- keep scoring history and PM publication history in separate immutable audit tables

## 7. Consistency Model

The application uses session-scoped transactional behavior via SQLAlchemy. Each API interaction or startup pipeline section operates within a managed session boundary.

Pilot posture:

- strong enough for a single-node demo system

Production recommendation:

- move to PostgreSQL with explicit transaction handling around pipeline jobs and PM publishing workflows

## 8. Migration Path To PostgreSQL

Migration is straightforward because:

- ORM models already define the logical contract
- SQLite-specific connection arguments are isolated in database configuration
- JSON fields already map naturally to PostgreSQL `jsonb`

Recommended migration steps:

1. provision PostgreSQL
2. move configuration from `database_url`
3. introduce migrations with Alembic
4. backfill initial reference and work-order data
5. validate pipeline output parity

## 9. Database Risks And Mitigations

### Risk: SQLite write contention

Mitigation:

- acceptable for pilot, replace in enterprise rollout

### Risk: No full analytics lineage history

Mitigation:

- add historical scoring and PM publication tables in phase two

### Risk: Rebuild model can overwrite current derived state

Mitigation:

- use staging tables and publish swaps in a productionized version