from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime
from typing import Generator

from sqlalchemy import JSON, Date, DateTime, Float, Integer, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from backend.config import get_settings


settings = get_settings()


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class Facility(Base):
    """Reference data for managed facilities."""

    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    facility_name: Mapped[str] = mapped_column(String(120), index=True)
    city: Mapped[str] = mapped_column(String(80))
    region: Mapped[str] = mapped_column(String(80))
    country: Mapped[str] = mapped_column(String(80), default="India")
    property_type: Mapped[str] = mapped_column(String(80))
    gross_area_sqft: Mapped[int] = mapped_column(Integer)
    criticality_tier: Mapped[str] = mapped_column(String(20))
    occupancy_band: Mapped[str] = mapped_column(String(30))


class Asset(Base):
    """Reference data for physical assets across facilities."""

    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    location_id: Mapped[str] = mapped_column(String(50), index=True)
    asset_name: Mapped[str] = mapped_column(String(120))
    asset_category: Mapped[str] = mapped_column(String(50), index=True)
    manufacturer: Mapped[str] = mapped_column(String(80))
    model_number: Mapped[str] = mapped_column(String(80))
    install_date: Mapped[date] = mapped_column(Date)
    health_index: Mapped[float] = mapped_column(Float)
    service_level: Mapped[str] = mapped_column(String(30))
    criticality_rank: Mapped[str] = mapped_column(String(20))


class Technician(Base):
    """Reference data for workforce planning and PM assignment."""

    __tablename__ = "technicians"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    technician_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    technician_name: Mapped[str] = mapped_column(String(120))
    primary_skill: Mapped[str] = mapped_column(String(80), index=True)
    region: Mapped[str] = mapped_column(String(80))
    shift: Mapped[str] = mapped_column(String(30))


class WorkOrder(Base):
    """Raw or normalized work orders ingested from the source system."""

    __tablename__ = "work_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    work_order_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    asset_id: Mapped[str] = mapped_column(String(50), index=True)
    location_id: Mapped[str] = mapped_column(String(50), index=True)
    problem_code: Mapped[str] = mapped_column(String(50), index=True)
    problem_description: Mapped[str] = mapped_column(String(255))
    created_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    closed_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    technician_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="Medium")
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    resolution_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    asset_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    asset_age_category: Mapped[str | None] = mapped_column(String(20), nullable=True)
    resolution_hours: Mapped[float] = mapped_column(Float, default=0.0)
    season_flag: Mapped[str | None] = mapped_column(String(20), nullable=True)


class PatternRecord(Base):
    """Detected recurring work-order patterns."""

    __tablename__ = "patterns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pattern_key: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    asset_id: Mapped[str] = mapped_column(String(50), index=True)
    location_id: Mapped[str] = mapped_column(String(50), index=True)
    problem_code: Mapped[str] = mapped_column(String(50), index=True)
    occurrence_count: Mapped[int] = mapped_column(Integer)
    avg_interval_days: Mapped[float] = mapped_column(Float)
    std_interval_days: Mapped[float] = mapped_column(Float)
    coefficient_of_variation: Mapped[float] = mapped_column(Float)
    regularity_score: Mapped[float] = mapped_column(Float, index=True)
    last_occurrence_date: Mapped[date] = mapped_column(Date)
    avg_resolution_hours: Mapped[float] = mapped_column(Float)
    avg_cost: Mapped[float] = mapped_column(Float)
    priority_mode: Mapped[str] = mapped_column(String(20))
    asset_category: Mapped[str] = mapped_column(String(50))
    asset_age_category: Mapped[str] = mapped_column(String(20))
    season_mode: Mapped[str] = mapped_column(String(20))
    assigned_skill_set: Mapped[str] = mapped_column(String(80))
    timeline: Mapped[list[str]] = mapped_column(JSON)


class PredictionRecord(Base):
    """Predictions for pattern recurrence."""

    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pattern_key: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    recurrence_probability_30d: Mapped[float] = mapped_column(Float)
    recurrence_probability_60d: Mapped[float] = mapped_column(Float)
    recurrence_probability_90d: Mapped[float] = mapped_column(Float)
    confidence_low: Mapped[float] = mapped_column(Float)
    confidence_high: Mapped[float] = mapped_column(Float)
    explanation: Mapped[dict] = mapped_column(JSON)


class PMSchedule(Base):
    """Generated PM schedules sent to the mock CAFM endpoint."""

    __tablename__ = "pm_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pattern_key: Mapped[str] = mapped_column(String(150), index=True)
    pm_title: Mapped[str] = mapped_column(String(200))
    frequency: Mapped[str] = mapped_column(String(30))
    next_due_date: Mapped[date] = mapped_column(Date)
    priority: Mapped[str] = mapped_column(String(20))
    estimated_duration: Mapped[float] = mapped_column(Float)
    assigned_skill_set: Mapped[str] = mapped_column(String(80))
    source_payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


engine = create_engine(settings.database_url, future=True, connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True, expire_on_commit=False)


def init_db() -> None:
    """Create all database tables."""

    Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional session scope."""

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def truncate_analytics(session: Session) -> None:
    """Clear derived analytics tables before regeneration."""

    session.query(PMSchedule).delete()
    session.query(PredictionRecord).delete()
    session.query(PatternRecord).delete()


def get_latest_counts(session: Session) -> dict[str, int]:
    """Return simple row counts for health and dashboard views."""

    counts = {
        "facilities": session.scalar(select(func.count()).select_from(Facility)) or 0,
        "assets": session.scalar(select(func.count()).select_from(Asset)) or 0,
        "technicians": session.scalar(select(func.count()).select_from(Technician)) or 0,
        "work_orders": session.scalar(select(func.count()).select_from(WorkOrder)) or 0,
        "patterns": session.scalar(select(func.count()).select_from(PatternRecord)) or 0,
        "predictions": session.scalar(select(func.count()).select_from(PredictionRecord)) or 0,
        "pm_schedules": session.scalar(select(func.count()).select_from(PMSchedule)) or 0,
    }
    return counts