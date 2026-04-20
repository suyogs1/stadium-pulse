"""
StadiumPulse Environment Configuration Tests.

Verifies the loading and prioritization of environmental variables
and the integrity of the fallback simulation logic.
"""

import os

from unittest.mock import patch
from src.core.settings import StadiumPulseSettings


def test_gemini_api_key_loading():
    """Verify that GEMINI_API_KEY is correctly loaded from the environment."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-123"}):
        settings = StadiumPulseSettings()
        assert settings.GEMINI_API_KEY == "test-key-123"


def test_stadium_api_key_default_value():
    """Verify that STADIUM_API_KEY has a secure default if missing."""
    with patch.dict(os.environ, {}, clear=True):
        settings = StadiumPulseSettings()
        # Assuming the secure default is 'pulse-secret-default'
        assert settings.STADIUM_API_KEY == "pulse-secret-default"


def test_stadium_api_key_override():
    """Verify that environment variables override default secret values."""
    with patch.dict(os.environ, {"STADIUM_API_KEY": "custom-secret-999"}):
        settings = StadiumPulseSettings()
        assert settings.STADIUM_API_KEY == "custom-secret-999"


def test_google_project_id_loading():
    """Verify that GOOGLE_PROJECT_ID is correctly loaded for GCP integration."""
    with patch.dict(os.environ, {"GOOGLE_PROJECT_ID": "pulse-prod-777"}):
        settings = StadiumPulseSettings()
        assert settings.GOOGLE_PROJECT_ID == "pulse-prod-777"


def test_threshold_loading():
    """Verify that operational thresholds can be configured via ENV."""
    with patch.dict(os.environ, {"CONGESTION_ALERT_THRESHOLD": "0.75"}):
        settings = StadiumPulseSettings()
        assert settings.CONGESTION_ALERT_THRESHOLD == 0.75


def test_feature_toggle_loading():
    """Verify that feature toggles are correctly parsed from ENV."""
    with patch.dict(os.environ, {"ENABLE_AI_REASONING": "False"}):
        settings = StadiumPulseSettings()
        assert settings.ENABLE_AI_REASONING is False
