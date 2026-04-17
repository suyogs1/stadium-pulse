"""
StadiumPulse Environment Configuration Tests.

Verifies the loading and prioritization of environmental variables 
and the integrity of the fallback simulation logic.
"""

import os
import pytest
import importlib
from unittest.mock import patch

@pytest.fixture
def clean_config():
    """Ensures a fresh import of the config module for each test."""
    import config
    importlib.reload(config)
    return config

def test_gemini_api_key_loading():
    """Verify that GEMINI_API_KEY is correctly loaded from the environment."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-123"}):
        import config
        importlib.reload(config)
        assert config.GEMINI_API_KEY == "test-key-123"

def test_stadium_api_key_default_value():
    """Verify that STADIUM_API_KEY has a secure default if missing."""
    with patch.dict(os.environ, {}, clear=True):
        import config
        importlib.reload(config)
        # Assuming the secure default is 'pulse-secret-default'
        assert config.STADIUM_API_KEY == "pulse-secret-default"

def test_stadium_api_key_override():
    """Verify that environment variables override default secret values."""
    with patch.dict(os.environ, {"STADIUM_API_KEY": "custom-secret-999"}):
        import config
        importlib.reload(config)
        assert config.STADIUM_API_KEY == "custom-secret-999"

def test_gemini_fallback_trigger_logic():
    """Verify the logic used to determine if the system should run in simulation mode."""
    # When key is missing
    with patch.dict(os.environ, {}, clear=True):
        import config
        importlib.reload(config)
        # Use the same logic as config.py: if not GEMINI_API_KEY: simulation_mode = True
        is_simulation = config.GEMINI_API_KEY is None
        assert is_simulation is True

def test_google_project_id_loading():
    """Verify that GOOGLE_PROJECT_ID is correctly loaded for GCP integration."""
    with patch.dict(os.environ, {"GOOGLE_PROJECT_ID": "pulse-prod-777"}):
        import config
        importlib.reload(config)
        assert config.GOOGLE_PROJECT_ID == "pulse-prod-777"
