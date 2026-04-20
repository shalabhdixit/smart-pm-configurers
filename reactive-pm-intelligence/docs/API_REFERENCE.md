# API Reference

Base URL:

```text
http://127.0.0.1:8000/api/v1
```

## 1. Authentication Model

Protected routes require a bearer token.

### Fetch Demo Token

`POST /auth/token`

Response:

```json
{
  "access_token": "innovate2026-demo-token",
  "token_type": "bearer"
}
```

Use the token in the `Authorization` header:

```text
Authorization: Bearer innovate2026-demo-token
```

## 2. Common Behavior

- Content type: `application/json`
- Auth: required unless explicitly noted
- Rate limiting: simple in-memory limit per client
- Error model: standard FastAPI HTTP error payloads

## 3. Endpoint Catalog

### 3.1 Ingestion

#### `POST /ingest`

Purpose: ingest a batch of work orders.

Request body:

```json
{
  "work_orders": [
    {
      "work_order_id": "WO-10001",
      "asset_id": "ASSET-001",
      "location_id": "LOC-01",
      "problem_code": "HVAC-001",
      "problem_description": "Air handling unit tripping intermittently",
      "created_date": "2026-04-01T10:00:00",
      "closed_date": "2026-04-01T13:00:00",
      "technician_id": "HV-001",
      "priority": "High",
      "cost": 4200,
      "resolution_code": "RESET",
      "asset_category": "HVAC",
      "asset_age_category": "mid",
      "resolution_hours": 3.0,
      "season_flag": "summer"
    }
  ]
}
```

Response:

```json
{
  "ingested": 1,
  "deduplicated": 0,
  "total_records": 5001
}
```

### 3.2 Pattern Intelligence

#### `GET /patterns`

Purpose: return all recurring patterns ordered by highest regularity score.

Response excerpt:

```json
[
  {
    "id": 1,
    "pattern_key": "ASSET-008|LOC-08|ELEC-011",
    "asset_id": "ASSET-008",
    "location_id": "LOC-08",
    "problem_code": "ELEC-011",
    "occurrence_count": 12,
    "avg_interval_days": 28.0,
    "regularity_score": 2.4849,
    "assigned_skill_set": "Electrical Specialist",
    "timeline": ["2025-01-12T00:00:00", "2025-02-09T00:00:00"]
  }
]
```

#### `GET /patterns/{pattern_id}`

Purpose: retrieve one pattern by identifier.

Returns `404` if the pattern does not exist.

### 3.3 Predictions

#### `GET /predictions`

Purpose: return recurrence predictions for all detected patterns.

Response excerpt:

```json
[
  {
    "id": 1,
    "pattern_key": "ASSET-008|LOC-08|ELEC-011",
    "recurrence_probability_30d": 0.891,
    "recurrence_probability_60d": 0.9603,
    "recurrence_probability_90d": 0.99,
    "confidence_low": 0.91,
    "confidence_high": 0.99,
    "explanation": {
      "avg_interval_days": 7.9231,
      "occurrence_count": 2.1435,
      "risk_score": 0.99,
      "model_auc_roc": 0.94
    }
  }
]
```

### 3.4 PM Automation

#### `POST /pm/generate`

Purpose: generate PM schedules for predictions above the configured threshold.

Response excerpt:

```json
{
  "generated_count": 15,
  "schedules": [
    {
      "id": 1,
      "pattern_key": "ASSET-008|LOC-08|ELEC-011",
      "pm_title": "Preventive: ELEC-011 for Asset ASSET-008",
      "frequency": "Monthly",
      "next_due_date": "2026-05-18",
      "priority": "Medium",
      "estimated_duration": 2.8,
      "assigned_skill_set": "Electrical Specialist"
    }
  ]
}
```

#### `GET /pm/schedules`

Purpose: return all PM schedules ordered by newest first.

### 3.5 Dashboard And Portfolio Views

#### `GET /dashboard/kpis`

Purpose: return dashboard KPI card metrics.

Response example:

```json
{
  "total_work_orders": 5000,
  "recurring_patterns": 16,
  "generated_pm_schedules": 15,
  "estimated_cost_savings": 18375.0,
  "predictions_next_30_days": 15,
  "top_pattern_key": "ASSET-008|LOC-08|ELEC-011"
}
```

#### `GET /work-orders`

Purpose: return the latest 100 work orders for live activity views.

#### `GET /portfolio/overview`

Purpose: return an executive-friendly overview of portfolio scale, top facilities, and at-risk assets.

Response excerpt:

```json
{
  "facilities": 50,
  "assets": 500,
  "technicians": 3492,
  "work_orders": 5000,
  "top_facilities": [
    {
      "location_id": "LOC-08",
      "facility_name": "Noida Smart Facility 08",
      "city": "Noida",
      "property_type": "Command Center",
      "reactive_work_orders": 115,
      "high_risk_patterns": 1,
      "open_pm_candidates": 1
    }
  ],
  "at_risk_assets": [
    {
      "asset_id": "ASSET-008",
      "asset_name": "Lift Asset 008",
      "location_id": "LOC-08",
      "asset_category": "Lift",
      "health_index": 83.2,
      "recurrence_probability_90d": 0.99,
      "recommended_action": "Trigger PM within 21 days"
    }
  ]
}
```

### 3.6 Assistant

#### `POST /assistant/chat`

Purpose: return a portfolio-aware assistant response using either a configured LLM provider or deterministic fallback mode.

Request example:

```json
{
  "action": "executive-summary",
  "message": "Summarize the live portfolio for SLT."
}
```

Response example:

```json
{
  "message": "Leadership summary:\n- The demo portfolio spans 50 facilities...",
  "provider": "mock",
  "model": "gemini-2.0-flash",
  "quick_actions": [
    {
      "id": "executive-summary",
      "label": "Executive Summary",
      "prompt": "Summarize the portfolio for leadership and focus on business impact."
    }
  ]
}
```

### 3.7 Operations

#### `GET /health`

Purpose: unauthenticated health and dependency summary.

Response example:

```json
{
  "status": "ok",
  "database": "connected",
  "metrics": {
    "facilities": 50,
    "assets": 500,
    "technicians": 3492,
    "work_orders": 5000,
    "patterns": 16,
    "predictions": 16,
    "pm_schedules": 15
  }
}
```

#### `GET /metrics`

Purpose: return raw row counts by domain table.

#### `POST /pipeline/run`

Purpose: rebuild the analytics pipeline from current work-order data.

Response example:

```json
{
  "patterns": 16,
  "predictions": 16,
  "schedules": 15
}
```

### 3.8 Integration

#### `GET /mock/cafm`

Purpose: return a simple readiness response for a mock CAFM endpoint.

Response:

```json
{
  "status": "ready",
  "message": "Mock CAFM endpoint available"
}
```

## 4. Error Semantics

- `401 Unauthorized`: missing or invalid bearer token.
- `404 Not Found`: requested pattern does not exist.
- `429 Too Many Requests`: simple rate limit exceeded.
- `422 Unprocessable Entity`: invalid payload shape.

## 5. Example PowerShell Session

```powershell
$token = (Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/auth/token").access_token
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/pipeline/run" -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/api/v1/portfolio/overview" -Headers @{ Authorization = "Bearer $token" }
```

## 6. API Design Notes

- The current API is optimized for pilot clarity over strict enterprise version negotiation.
- Dashboard endpoints expose aggregation already shaped for UI consumption.
- Assistant responses intentionally return provider metadata so demos can prove live versus deterministic mode.