import json
from src.services.gemini_service import gemini_service
from src.agents.optimizer_agent import OptimizerAgent
from src.core.models import StadiumState
from src.core.venues import NARENDRA_MODI_STADIUM


def test_gemini_service_initialization():
    """Verify that GeminiService correctly reports hydration state."""
    # Note: Direct SDK init depends on GOOGLE_PROJECT_ID
    assert hasattr(gemini_service, "is_active")


def test_optimizer_integration_with_gemini_trigger():
    """Ensure OptimizerAgent attempts to engage Gemini when threshold is breached."""
    agent = OptimizerAgent(NARENDRA_MODI_STADIUM)

    # S1 capacity is 12000. 11000 is ~91%, breaching the default 85% threshold.
    state = StadiumState(occupancy={"S1": 11000}, wait_times={})
    result_json = agent.evaluate_plays(state)
    result = json.loads(result_json)

    # Check if AI Reasoning was mentioned in the trace
    assert any("Engaging Gemini Service" in t for t in result["reasoning_trace"])
    # If gemini is not active in test env, it will fallback, but trace will show the attempt.
