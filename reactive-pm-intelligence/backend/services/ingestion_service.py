from __future__ import annotations

from collections.abc import Iterable

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.database import WorkOrder
from backend.models.schemas import WorkOrderIn
from backend.utils.helpers import season_from_date


REQUIRED_COLUMNS = {
    "work_order_id",
    "asset_id",
    "location_id",
    "problem_code",
    "problem_description",
    "created_date",
    "closed_date",
    "technician_id",
    "priority",
    "cost",
    "resolution_code",
}


def load_dataframe(path: str) -> pd.DataFrame:
    """Load a CSV or JSON work-order extract."""

    if path.endswith(".json"):
        df = pd.read_json(path)
    else:
        df = pd.read_csv(path)
    return normalize_work_orders(df)


def normalize_work_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize and clean incoming work-order data."""

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    normalized = df.copy()
    normalized["created_date"] = pd.to_datetime(normalized["created_date"], errors="coerce")
    normalized["closed_date"] = pd.to_datetime(normalized["closed_date"], errors="coerce")
    normalized = normalized.dropna(subset=["work_order_id", "asset_id", "location_id", "problem_code", "created_date"])
    normalized["priority"] = normalized["priority"].fillna("Medium").astype(str).str.title()
    normalized["problem_code"] = normalized["problem_code"].astype(str).str.upper()
    normalized["asset_id"] = normalized["asset_id"].astype(str).str.upper()
    normalized["location_id"] = normalized["location_id"].astype(str).str.upper()
    normalized["problem_description"] = normalized["problem_description"].fillna("Unknown issue").astype(str)
    normalized["cost"] = pd.to_numeric(normalized["cost"], errors="coerce").fillna(0.0)
    normalized["resolution_hours"] = pd.to_numeric(normalized.get("resolution_hours", 0.0), errors="coerce").fillna(0.0)
    normalized["resolution_code"] = normalized["resolution_code"].where(normalized["resolution_code"].notna(), None)
    normalized["technician_id"] = normalized["technician_id"].where(normalized["technician_id"].notna(), None)
    normalized["asset_category"] = normalized.get("asset_category", "General").fillna("General")
    normalized["asset_age_category"] = normalized.get("asset_age_category", "mid").fillna("mid")
    normalized["season_flag"] = normalized.apply(
        lambda row: row.get("season_flag") or season_from_date(row["created_date"]),
        axis=1,
    )
    normalized = normalized.sort_values("created_date").drop_duplicates(subset=["work_order_id"], keep="last")
    return normalized


def ingest_work_orders(session: Session, work_orders: Iterable[WorkOrderIn] | pd.DataFrame) -> dict[str, int]:
    """Upsert a collection of work orders into the database."""

    if isinstance(work_orders, pd.DataFrame):
        normalized_frame = normalize_work_orders(work_orders)
        records = [WorkOrderIn(**record) for record in normalized_frame.to_dict(orient="records")]
    else:
        records = list(work_orders)

    existing_ids = set(session.scalars(select(WorkOrder.work_order_id)).all())
    ingested = 0
    deduplicated = 0
    for item in records:
        if item.work_order_id in existing_ids:
            deduplicated += 1
            continue
        session.add(
            WorkOrder(
                work_order_id=item.work_order_id,
                asset_id=item.asset_id,
                location_id=item.location_id,
                problem_code=item.problem_code,
                problem_description=item.problem_description,
                created_date=item.created_date,
                closed_date=item.closed_date,
                technician_id=item.technician_id,
                priority=item.priority,
                cost=item.cost,
                resolution_code=item.resolution_code,
                asset_category=item.asset_category or "General",
                asset_age_category=item.asset_age_category or "mid",
                resolution_hours=item.resolution_hours,
                season_flag=item.season_flag or season_from_date(item.created_date),
            )
        )
        ingested += 1
    session.flush()
    total_records = session.query(WorkOrder).count()
    return {"ingested": ingested, "deduplicated": deduplicated, "total_records": total_records}