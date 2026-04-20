from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.config import get_settings
from backend.models.database import init_db, session_scope
from backend.scheduler import create_scheduler
from backend.services.portfolio_service import sync_reference_entities
from backend.services.ingestion_service import ingest_work_orders, load_dataframe
from backend.utils.logger import configure_logging


settings = get_settings()
scheduler = create_scheduler()


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    init_db()
    if settings.sample_data_path.exists():
        dataframe = load_dataframe(str(settings.sample_data_path))
        with session_scope() as session:
            ingest_work_orders(session, dataframe)
            sync_reference_entities(session)
    if not scheduler.running:
        scheduler.start()
    yield
    if scheduler.running:
        scheduler.shutdown(wait=False)


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_origin,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"app": settings.app_name, "version": settings.app_version, "status": "running"}