import pytest
import logging
import json
from src.services.gemini_reasoner import gemini_ai
from src.agents.optimizer_agent import OptimizerAgent
from config import NARENDRA_MODI_STADIUM, StadiumState

def test_gemini_threshold_trigger():
    """Verify Gemini reasoning logic for different occupancy levels."""
    # Simulation mode fallback logic check
    # Under 85%
    data_low = {"occupancy_perc": {"S1": 0.5}}
    res_low = gemini_ai.get_strategic_play(data_low)
    assert "Monitor Only" in res_low
    
    # Over 85%
    data_high = {"occupancy_perc": {"S1": 0.88}}
    res_high = gemini_ai.get_strategic_play(data_high)
    assert "Direct Reroute" in res_high
    
    # Critical (Over 95%)
    data_crit = {"occupancy_perc": {"S1": 0.98}}
    res_crit = gemini_ai.get_strategic_play(data_crit)
    assert "Predictive Buffer" in res_crit

def test_gemini_caching(caplog):
    """Verify that identical states result in a cache hit."""
    data = {"peak_load": 0.90, "occupancy_perc": {"S1": 0.90}}
    
    # Initial call to populate cache
    gemini_ai._execution_cache.clear()
    gemini_ai.get_strategic_play(data)
    
    # Second call - Should result in a Cache HIT
    import logging
    # The logger logs "Cache HIT" at INFO level in my implementation
    # Check the implementation: logger.info("GeminiAI: Cache HIT. Returning stored reasoning.")
    with caplog.at_level(logging.INFO):
        gemini_ai.get_strategic_play(data)
        assert "Cache HIT" in caplog.text

def test_optimizer_integration_with_gemini():
    """Ensure OptimizerAgent correctly calls Gemini when threshold is breached."""
    agent = OptimizerAgent(NARENDRA_MODI_STADIUM)
    
    # Breach threshold (88% load)
    # S1 capacity is 12000. 11000 is > 88% (roughly 91%).
    state = StadiumState(occupancy={"S1": 11000}, wait_times={})
    result = json.loads(agent.evaluate_plays(state))
    
    assert any("Engaging Gemini Engine" in t for t in result["reasoning_trace"])
    assert any("GEMINI_REASONER Trace" in t for t in result["reasoning_trace"])
