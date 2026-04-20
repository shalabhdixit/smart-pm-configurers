from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.models.database import PMSchedule, PatternRecord, PredictionRecord, WorkOrder, get_db, get_latest_counts, truncate_analytics
from backend.models.schemas import AssistantRequest, AssistantResponse, AuthTokenResponse, GeneratePMResponse, HealthResponse, IngestRequest, IngestResponse, KPIResponse, PatternResponse, PMScheduleResponse, PortfolioOverviewResponse, PredictionResponse
from backend.services.assistant_service import generate_assistant_response
from backend.services.ingestion_service import ingest_work_orders
from backend.services.pattern_engine import build_work_order_dataframe, detect_recurring_patterns, persist_patterns
from backend.services.portfolio_service import build_portfolio_overview, sync_reference_entities
from backend.services.pm_generator import generate_pm_schedules
from backend.services.prediction_engine import predict_patterns


router = APIRouter(prefix="/api/v1")
settings = get_settings()
security = HTTPBearer(auto_error=False)
REQUEST_WINDOWS: dict[str, list[datetime]] = defaultdict(list)


def authenticate(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> str:
    """Validate the demo bearer token."""

    if credentials is None or credentials.credentials != settings.api_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing bearer token")
    return credentials.credentials


DbSession = Annotated[Session, Depends(get_db)]
AuthToken = Annotated[str, Depends(authenticate)]


def enforce_rate_limit(request: Request) -> None:
    """Apply a simple in-memory rate limit."""

    client = request.client.host if request.client else "anonymous"
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=1)
    REQUEST_WINDOWS[client] = [stamp for stamp in REQUEST_WINDOWS[client] if stamp >= cutoff]
    if len(REQUEST_WINDOWS[client]) >= settings.rate_limit_per_minute:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
    REQUEST_WINDOWS[client].append(now)


@router.post("/auth/token", tags=["auth"])
async def get_demo_token() -> AuthTokenResponse:
    return AuthTokenResponse(access_token=settings.api_token)


@router.post("/ingest", tags=["ingestion"])
async def ingest_endpoint(payload: IngestRequest, request: Request, db: DbSession, _: AuthToken) -> IngestResponse:
    enforce_rate_limit(request)
    result = ingest_work_orders(db, payload.work_orders)
    return IngestResponse(**result)


@router.get("/patterns", tags=["patterns"])
async def list_patterns(request: Request, db: DbSession, _: AuthToken) -> list[PatternResponse]:
    enforce_rate_limit(request)
    patterns = db.scalars(select(PatternRecord).order_by(PatternRecord.regularity_score.desc())).all()
    return [PatternResponse.model_validate(pattern) for pattern in patterns]


@router.get("/patterns/{pattern_id}", tags=["patterns"], responses={404: {"description": "Pattern not found"}})
async def get_pattern(pattern_id: int, request: Request, db: DbSession, _: AuthToken) -> PatternResponse:
    enforce_rate_limit(request)
    pattern = db.get(PatternRecord, pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    return PatternResponse.model_validate(pattern)


@router.get("/predictions", tags=["predictions"])
async def list_predictions(request: Request, db: DbSession, _: AuthToken) -> list[PredictionResponse]:
    enforce_rate_limit(request)
    predictions = db.scalars(select(PredictionRecord).order_by(PredictionRecord.recurrence_probability_90d.desc())).all()
    return [PredictionResponse.model_validate(prediction) for prediction in predictions]


@router.post("/pm/generate", tags=["pm"])
async def generate_pm(request: Request, db: DbSession, _: AuthToken) -> GeneratePMResponse:
    enforce_rate_limit(request)
    schedules = generate_pm_schedules(db)
    return GeneratePMResponse(generated_count=len(schedules), schedules=[PMScheduleResponse.model_validate(item) for item in schedules])


@router.get("/pm/schedules", tags=["pm"])
async def list_pm_schedules(request: Request, db: DbSession, _: AuthToken) -> list[PMScheduleResponse]:
    enforce_rate_limit(request)
    schedules = db.scalars(select(PMSchedule).order_by(PMSchedule.created_at.desc())).all()
    return [PMScheduleResponse.model_validate(schedule) for schedule in schedules]


@router.get("/dashboard/kpis", tags=["dashboard"])
async def dashboard_kpis(request: Request, db: DbSession, _: AuthToken) -> KPIResponse:
    enforce_rate_limit(request)
    sync_reference_entities(db)
    counts = get_latest_counts(db)
    next_30_predictions = db.scalars(select(PredictionRecord).where(PredictionRecord.recurrence_probability_30d >= settings.pm_probability_threshold)).all()
    top_pattern = db.scalars(select(PatternRecord).order_by(PatternRecord.regularity_score.desc())).first()
    estimated_savings = round(counts["pm_schedules"] * 3500.0 * 0.35, 2)
    return KPIResponse(
        total_work_orders=counts["work_orders"],
        recurring_patterns=counts["patterns"],
        generated_pm_schedules=counts["pm_schedules"],
        estimated_cost_savings=estimated_savings,
        predictions_next_30_days=len(next_30_predictions),
        top_pattern_key=top_pattern.pattern_key if top_pattern else None,
    )


@router.get("/health", tags=["ops"])
async def health(db: DbSession) -> HealthResponse:
    counts = get_latest_counts(db)
    return HealthResponse(status="ok", database="connected", metrics=counts)


@router.get("/metrics", tags=["ops"])
async def metrics(db: DbSession) -> dict[str, int]:
    return get_latest_counts(db)


@router.post("/pipeline/run", tags=["ops"])
async def run_pipeline(request: Request, db: DbSession, _: AuthToken) -> dict[str, int]:
    enforce_rate_limit(request)
    truncate_analytics(db)
    sync_reference_entities(db)
    work_orders = build_work_order_dataframe(db)
    patterns_df = detect_recurring_patterns(work_orders)
    persist_patterns(db, patterns_df)
    predictions = predict_patterns(db)
    schedules = generate_pm_schedules(db)
    return {"patterns": len(patterns_df), "predictions": len(predictions), "schedules": len(schedules)}


@router.get("/mock/cafm", tags=["integration"])
async def mock_cafm() -> dict[str, str]:
    return {"status": "ready", "message": "Mock CAFM endpoint available"}


@router.get("/work-orders", tags=["ingestion"])
async def list_work_orders(request: Request, db: DbSession, _: AuthToken) -> list[dict[str, Any]]:
    enforce_rate_limit(request)
    rows = db.scalars(select(WorkOrder).order_by(WorkOrder.created_date.desc()).limit(100)).all()
    return [{"work_order_id": row.work_order_id, "asset_id": row.asset_id, "problem_code": row.problem_code, "created_date": row.created_date.isoformat(), "priority": row.priority, "cost": row.cost} for row in rows]


@router.get("/portfolio/overview", tags=["portfolio"])
async def portfolio_overview(request: Request, db: DbSession, _: AuthToken) -> PortfolioOverviewResponse:
    enforce_rate_limit(request)
    sync_reference_entities(db)
    return PortfolioOverviewResponse(**build_portfolio_overview(db))


@router.post("/assistant/chat", tags=["assistant"])
async def assistant_chat(payload: AssistantRequest, request: Request, db: DbSession, _: AuthToken) -> AssistantResponse:
    enforce_rate_limit(request)
    sync_reference_entities(db)
    response = await generate_assistant_response(db, payload)
    return AssistantResponse(**response)