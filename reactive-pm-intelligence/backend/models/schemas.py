from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WorkOrderIn(BaseModel):
    """Incoming work-order payload."""

    work_order_id: str
    asset_id: str
    location_id: str
    problem_code: str
    problem_description: str
    created_date: datetime
    closed_date: datetime | None = None
    technician_id: str | None = None
    priority: str = "Medium"
    cost: float = 0.0
    resolution_code: str | None = None
    asset_category: str | None = None
    asset_age_category: str | None = None
    resolution_hours: float = 0.0
    season_flag: str | None = None


class IngestRequest(BaseModel):
    """Batch ingestion request."""

    work_orders: list[WorkOrderIn]


class IngestResponse(BaseModel):
    ingested: int
    deduplicated: int
    total_records: int


class PatternResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pattern_key: str
    asset_id: str
    location_id: str
    problem_code: str
    occurrence_count: int
    avg_interval_days: float
    std_interval_days: float
    coefficient_of_variation: float
    regularity_score: float
    last_occurrence_date: date
    avg_resolution_hours: float
    avg_cost: float
    priority_mode: str
    asset_category: str
    asset_age_category: str
    season_mode: str
    assigned_skill_set: str
    timeline: list[str]


class PredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pattern_key: str
    recurrence_probability_30d: float
    recurrence_probability_60d: float
    recurrence_probability_90d: float
    confidence_low: float
    confidence_high: float
    explanation: dict[str, float]


class PMScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pattern_key: str
    pm_title: str
    frequency: str
    next_due_date: date
    priority: str
    estimated_duration: float
    assigned_skill_set: str
    source_payload: dict[str, Any]
    created_at: datetime


class KPIResponse(BaseModel):
    total_work_orders: int
    recurring_patterns: int
    generated_pm_schedules: int
    estimated_cost_savings: float
    predictions_next_30_days: int
    top_pattern_key: str | None = None


class HealthResponse(BaseModel):
    status: str
    database: str
    metrics: dict[str, int]


class GeneratePMResponse(BaseModel):
    generated_count: int
    schedules: list[PMScheduleResponse]


class AuthTokenResponse(BaseModel):
    access_token: str = Field(serialization_alias="access_token")
    token_type: str = "bearer"


class AssistantAction(BaseModel):
    id: str
    label: str
    prompt: str


class AssistantRequest(BaseModel):
    message: str = ""
    action: str | None = None


class AssistantResponse(BaseModel):
    message: str
    provider: str
    model: str
    quick_actions: list[AssistantAction]


class FacilitySummary(BaseModel):
    location_id: str
    facility_name: str
    city: str
    property_type: str
    reactive_work_orders: int
    high_risk_patterns: int
    open_pm_candidates: int


class AssetSummary(BaseModel):
    asset_id: str
    asset_name: str
    location_id: str
    asset_category: str
    health_index: float
    recurrence_probability_90d: float
    recommended_action: str


class PortfolioOverviewResponse(BaseModel):
    facilities: int
    assets: int
    technicians: int
    work_orders: int
    top_facilities: list[FacilitySummary]
    at_risk_assets: list[AssetSummary]