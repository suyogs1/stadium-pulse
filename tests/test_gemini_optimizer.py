"""
StadiumPulse Gemini Integration Unit Tests.

Verifies the intelligent hand-off between heuristic logic and Gemini AI 
during high-congestion scenarios.
"""

import pytest
import json
from unittest.mock import MagicMock, patch
from config import NARENDRA_MODI_STADIUM, StadiumState
from src.agents.optimizer_agent import OptimizerAgent

@pytest.fixture
def agent():
    return OptimizerAgent(NARENDRA_MODI_STADIUM)

@patch("src.agents.optimizer_agent.gemini_ai")
def test_gemini_trigger_threshold(mock_gemini, agent):
    """Verify Gemini is ONLY called when peak occupancy > 85%."""
    
    # CASE 1: 80% occupancy (Should NOT trigger Gemini)
    # S1 capacity is 12000 in test config usually. 
    # Let's be explicit with the config scale.
    s1_cap = NARENDRA_MODI_STADIUM.sections[0].capacity
    state_low = StadiumState(occupancy={"S1": int(s1_cap * 0.8)}, wait_times={})
    
    agent.evaluate_plays(state_low)
    mock_gemini.get_strategic_play.assert_not_called()
    
    # CASE 2: 90% occupancy (Should trigger Gemini)
    state_high = StadiumState(occupancy={"S1": int(s1_cap * 0.9)}, wait_times={})
    # Mocking the AI return string
    mock_gemini.get_strategic_play.return_value = "REASONING: Risk detected. STRATEGY: Direct Reroute."
    
    agent.evaluate_plays(state_high)
    mock_gemini.get_strategic_play.assert_called_once()

@patch("src.agents.optimizer_agent.gemini_ai")
def test_gemini_response_parsing(mock_gemini, agent):
    """Verify structured metadata extraction from Gemini strings."""
    s1_cap = NARENDRA_MODI_STADIUM.sections[0].capacity
    state_high = StadiumState(occupancy={"S1": int(s1_cap * 0.9)}, wait_times={})
    
    # Mock a complex reasoning string
    mock_gemini.get_strategic_play.return_value = (
        "REASONING: Sector S1 reached 90%. Adjacency matrix suggests S2 is clear. "
        "STRATEGY: Direct Reroute."
    )
    
    result_json = agent.evaluate_plays(state_high)
    result = json.loads(result_json)
    
    assert result["is_ai_decision"] is True
    assert result["ai_metadata"]["decision"] == "REROUTE"
    assert "S1 reached 90%" in result["ai_metadata"]["observation"]

@patch("src.agents.optimizer_agent.gemini_ai")
def test_fallback_simulation_logic(mock_gemini, agent):
    """Verify that the system gracefully handles inactive API states."""
    mock_gemini.api_active = False # Simulate missing key
    
    s1_cap = NARENDRA_MODI_STADIUM.sections[0].capacity
    state_high = StadiumState(occupancy={"S1": int(s1_cap * 0.9)}, wait_times={})
    
    # The agent should still call the method, but the reasoner itself 
    # should return a simulation-style string.
    mock_gemini.get_strategic_play.return_value = "REASONING: [SIMULATION] STRATEGY: Monitor Only."
    
    result_json = agent.evaluate_plays(state_high)
    result = json.loads(result_json)
    
    assert result["is_ai_decision"] is True # It still attempted AI logic
    assert result["action_type"] == "MONITOR_ONLY"
