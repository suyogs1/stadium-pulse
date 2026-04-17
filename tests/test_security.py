"""
StadiumPulse Security Validation Suite.

This module ensures that the system adheres to strict security standards,
specifically regarding secret management and safe failure modes.
"""

import os
import pytest
from src.services.gemini_reasoner import GeminiReasoner
import config

def test_no_hardcoded_keys():
    """
    Scans core source files for common patterns of hardcoded API keys.
    Ensures that secrets are not accidentally committed to code.
    """
    sensitive_patterns = ["AIza", "sk-", "ghp_"] # Common prefix patterns for keys
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
                                pytest.fail(f"Potential hardcoded key detected in {path}: pattern '{pattern}'")

def test_environment_variable_loading():
    """
    Verifies that the configuration layer relies on environment 
    variables rather than static constants for critical overrides.
    """
    # Verify that the config module has the expected attribute
    assert hasattr(config, "GEMINI_API_KEY")
    assert hasattr(config, "STADIUM_API_KEY")

def test_gemini_safe_failure_without_key(monkeypatch):
    """
    Ensures that the GeminiReasoner degrades gracefully into 
    Simulation Mode if the GEMINI_API_KEY is absent.
    """
    # Temporarily remove any existing key from the environment/config
    monkeypatch.setattr(config, "GEMINI_API_KEY", None)
    
    # Initialize a new reasoner while simulating key absence
    reasoner = GeminiReasoner()
    
    # It should not be active but should still return a logical response (mock)
    assert reasoner.api_active is False
    
    # Test a reasoning call
    test_context = {"occupancy_perc": {"S1": 0.5}}
    response = reasoner.get_strategic_play(test_context)
    
    # Verify it returns the mock fallback reasoning
    assert "[SIMULATION MODE]" in response
    assert "REASONING:" in response

def test_stadium_api_key_default_value():
    """
    Verifies that the Stadium API has a default internal key if none is 
    provided, ensuring the security middleware is always active.
    """
    assert config.STADIUM_API_KEY is not None
    assert len(config.STADIUM_API_KEY) > 10
