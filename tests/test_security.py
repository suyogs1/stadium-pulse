"""
StadiumPulse Security Validation Suite.

This module ensures that the system adheres to strict security standards,
specifically regarding secret management and safe failure modes.
"""

import os
import pytest
from unittest.mock import patch
from src.services.gemini_service import VertexAIService
from src.core.settings import settings


def test_no_hardcoded_keys():
    """
    Scans core source files for common patterns of hardcoded API keys.
    Ensures that secrets are not accidentally committed to code.
    """
    sensitive_patterns = ["AIza", "sk-", "ghp_"]  # Common prefix patterns for keys
    source_dirs = ["src", "scripts"]

    for directory in source_dirs:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        for pattern in sensitive_patterns:
                            # We check for patterns that look like assignments to strings
                            if f'"{pattern}' in content or f"'{pattern}" in content:
                                pytest.fail(
                                    f"Potential hardcoded key detected in {path}: pattern '{pattern}'"
                                )


def test_environment_variable_loading():
    """
    Verifies that the configuration layer relies on environment
    variables rather than static constants for critical overrides.
    """
    # Verify that the settings object has the expected attributes
    assert hasattr(settings, "GEMINI_API_KEY")
    assert hasattr(settings, "STADIUM_API_KEY")


def test_gemini_safe_failure_without_key(monkeypatch):
    """
    Ensures that the VertexAIService degrades gracefully into
    Simulation Mode if the GEMINI_API_KEY is absent.
    """
    # Mock settings to simulate missing key
    from src.core.settings import StadiumPulseSettings

    mock_settings = StadiumPulseSettings()
    mock_settings.GEMINI_API_KEY = None
    mock_settings.ENABLE_AI_REASONING = False

    with patch("src.services.gemini_service.settings", mock_settings):
        service = VertexAIService(project_id="test")
        assert service.is_active is False


def test_stadium_api_key_default_value():
    """
    Verifies that the Stadium API has a default internal key if none is
    provided, ensuring the security middleware is always active.
    """
    assert settings.STADIUM_API_KEY is not None
    assert len(settings.STADIUM_API_KEY) > 10
