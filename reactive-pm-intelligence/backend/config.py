from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8")

    app_name: str = "Reactive to PM Intelligence"
    app_version: str = "1.0.0"
    environment: str = "development"
    database_url: str = f"sqlite:///{(BASE_DIR / 'data' / 'reactive_pm.db').as_posix()}"
    api_token: str = "innovate2026-demo-token"
    frontend_origin: str = "http://127.0.0.1:5500"
    rate_limit_per_minute: int = 100
    recurring_min_occurrences: int = 3
    recurring_max_interval_days: int = 180
    pm_probability_threshold: float = 0.70
    random_seed: int = 42
    model_path: Path = BASE_DIR / "ml" / "model_artifacts" / "recurrence_model.pkl"
    sample_data_path: Path = BASE_DIR / "data" / "sample_work_orders.csv"
    generated_db_path: Path = BASE_DIR / "data" / "reactive_pm.db"
    mock_cafm_webhook: str = Field(default="http://localhost:8000/api/v1/mock/cafm")
    llm_provider: str = "mock"
    llm_api_key: str | None = None
    llm_model: str = "gemini-2.0-flash"
    llm_base_url: str | None = None
    llm_timeout_seconds: float = 20.0
    assistant_top_patterns: int = 5
    assistant_top_facilities: int = 3


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings object."""

    return Settings()