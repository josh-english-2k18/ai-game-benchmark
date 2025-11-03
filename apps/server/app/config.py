from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    cors_origins: str = "http://localhost:3000"
    telemetry_log_path: Path = Path("bench/logs/telemetry.ndjson")
    metrics_window: int = 512
    default_backend: str = "cpu"
    debug_mode: bool = False

    model_config = SettingsConfigDict(env_prefix="AIGB_", env_file=".env", case_sensitive=False)


settings = Settings()
