"""
StadiumPulse Gemini Integration Unit Tests.

Verifies the intelligent hand-off between heuristic logic and Gemini AI
during high-congestion scenarios.
"""

import pytest
import json
from unittest.mock import patch
from src.core.models import StadiumState
from src.core.venues import NARENDRA_MODI_STADIUM
from src.agents.optimizer_agent import OptimizerAgent


@pytest.fixture
def agent():
    return OptimizerAgent(NARENDRA_MODI_STADIUM)


@patch("src.agents.optimizer_agent.gemini_service")
def test_gemini_trigger_threshold(mock_gemini, agent):
    """Verify Gemini is ONLY called when peak occupancy > 85%."""

    # CASE 1: 80% occupancy (Should NOT trigger Gemini)
    s1_cap = NARENDRA_MODI_STADIUM.sections[0].capacity
    state_low = StadiumState(occupancy={"S1": int(s1_cap * 0.8)}, wait_times={})

    agent.evaluate_plays(state_low)
    mock_gemini.execute_strategic_analysis.assert_not_called()

    # CASE 2: 90% occupancy (Should trigger Gemini)
    state_high = StadiumState(occupancy={"S1": int(s1_cap * 0.9)}, wait_times={})
    # Mocking the AI return string
    mock_gemini.execute_strategic_analysis.return_value = (
        "REASONING: Risk detected. STRATEGY: Direct Reroute."
    )

    agent.evaluate_plays(state_high)
    mock_gemini.execute_strategic_analysis.assert_called_once()


@patch("src.agents.optimizer_agent.gemini_service")
def test_gemini_reponse_influence(mock_gemini, agent):
    """Verify that Gemini's response influences the agent's action selection."""
    s1_cap = NARENDRA_MODI_STADIUM.sections[0].capacity
    state_high = StadiumState(occupancy={"S1": int(s1_cap * 0.9)}, wait_times={})

    # Scenario: Gemini suggests a Predictive Buffer
    mock_gemini.execute_strategic_analysis.return_value = (
        "REASONING: [Neural] STRATEGY: Predictive Buffer."
    )

    result_json = agent.evaluate_plays(state_high)
    result = json.loads(result_json)

    assert result["is_ai_decision"] is True
    assert result["action_type"] == "PREDICTIVE_BUFFER"


@patch("src.agents.optimizer_agent.gemini_service")
def test_fallback_simulation_logic(mock_gemini, agent):
    """Verify that the system gracefully handles inactive API states."""
    # The agent calls it regardless if threshold is met, the service handles its own state
    s1_cap = NARENDRA_MODI_STADIUM.sections[0].capacity
    state_high = StadiumState(occupancy={"S1": int(s1_cap * 0.9)}, wait_times={})

    # Mocking a fallback-style response
    mock_gemini.execute_strategic_analysis.return_value = (
        "REASONING: [FALLBACK] STRATEGY: Monitor Only."
    )

    result_json = agent.evaluate_plays(state_high)
    result = json.loads(result_json)

    assert result["is_ai_decision"] is True  # It still attempted AI logic
    # Safety Heuristic: Even if AI says MONITOR_ONLY, 90% load triggers PREDICTIVE_BUFFER fallback
    assert result["action_type"] == "PREDICTIVE_BUFFER"
