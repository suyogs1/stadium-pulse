"""
StadiumPulse Centralized Settings Layer: Pydantic BaseSettings Orchestration.

Manages environment-level security keys, operational thresholds,
and feature toggles across the entire agentic ecosystem.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class StadiumPulseSettings(BaseSettings):
    """
    Enterprise-grade settings management using environment variable injection.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    # --- Security & Integration Keys ---
    GOOGLE_PROJECT_ID: str = "stadium-pulse-dev"
    STADIUM_API_KEY: str = "pulse-secret-default"
    GEMINI_API_KEY: Optional[str] = None
    TRANSLATE_API_KEY: Optional[str] = None
    RECAPTCHA_SECRET: Optional[str] = None
    MAPS_API_KEY: Optional[str] = None
    GA4_MEASUREMENT_ID: Optional[str] = None

    # --- Operational Thresholds (The "Tuning" Dial) ---
    CONGESTION_ALERT_THRESHOLD: float = 0.85
    WAIT_TIME_THRESHOLD_MINUTES: float = 15.0
    INCENTIVE_BUDGET_HOURLY: int = 1000

    # --- Feature Toggles ---
    ENABLE_AI_REASONING: bool = True
    ENABLE_CLOUD_LOGGING: bool = True
    ENABLE_PUBSUB_PIPELINE: bool = True


# Global Settings Singleton
settings: StadiumPulseSettings = StadiumPulseSettings()
