import pytest
import json
from src.agents.optimizer_agent import OptimizerAgent
from src.core.models import StadiumState, StadiumConfig, Section, Gate
from src.core.venues import NARENDRA_MODI_STADIUM


@pytest.fixture
def agent():
    return OptimizerAgent(NARENDRA_MODI_STADIUM, max_incentives_budget=100)


def test_goal_initialization_trace(agent):
    """Verify that reasoning trace includes strategic goal initialization."""
    state = StadiumState(occupancy={"S1": 100}, wait_times={})
    result = json.loads(agent.evaluate_plays(state))

    trace = result["reasoning_trace"]
    assert any("Goal Initialization" in t for t in trace)
    assert any("Minimizing Crowd Density Variance" in t for t in trace)


def test_monitor_only_strategic_reasoning(agent):
    """Test 'Monitor Only' output for strategic self-awareness."""
    state = StadiumState(occupancy={"S1": 5000}, wait_times={"G1": 5.0})
    result = json.loads(agent.evaluate_plays(state))

    assert result["action_type"] == "MONITOR_ONLY"
    assert any("MONITOR_ONLY strategy engaged" in t for t in result["reasoning_trace"])


def test_incentive_budget_depletion_logic(agent):
    """Test edge case where budget is exactly depleted."""
    # Each incentive costs 10 per concession.
    # Current config has 6 concessions.
    high_waits = {f"C{i}": 20.0 for i in range(1, 7)}
    state = StadiumState(occupancy={}, wait_times=high_waits)

    # 6 concessions * 10 = 60 budget
    result1 = json.loads(agent.evaluate_plays(state))
    assert result1["action_type"] == "INCENTIVIZE"
    assert result1["budget_remaining"] == 40

    # Deplete the rest
    agent.budget_remaining = 0
    result2 = json.loads(agent.evaluate_plays(state))
    assert result2["action_type"] == "MONITOR_ONLY"
    assert any("Budget exhausted" in t for t in result2["reasoning_trace"])


def test_no_alternative_gates_available():
    """Test REROUTE when all gates are jammed."""
    custom_config = StadiumConfig(
        stadium_name="Full Jam",
        sections=[Section(section_id="S1", name="S1", capacity=100, adjacency_matrix={})],
        gates=[Gate(gate_id="G1", name="G1")],  # Only one gate
        concession_blocks=[],
    )
    test_agent = OptimizerAgent(custom_config)
    state = StadiumState(occupancy={}, wait_times={"G1": 25.0})

    result = json.loads(test_agent.evaluate_plays(state))
    assert result["action_type"] == "REROUTE"
    assert any("No alternative gates available" in t for t in result["reasoning_trace"])


def test_budget_reset_logic(agent):
    """Verify that budget resets after 1 hour."""
    agent.budget_remaining = 10
    # Mock the reset time to be in the past
    from datetime import datetime, timedelta

    agent.budget_reset_time = datetime.now() - timedelta(minutes=1)

    # Next call should trigger reset
    state = StadiumState(occupancy={}, wait_times={})
    agent.evaluate_plays(state)
    assert agent.budget_remaining == agent.max_incentives_budget


def test_reroute_adjacency_selection(agent):
    """Verify REROUTE picks the closest available gate mapping."""
    # Gate 1 jam
    state = StadiumState(occupancy={}, wait_times={"G1": 25.0})
    result = json.loads(agent.evaluate_plays(state))

    assert result["action_type"] == "REROUTE"
    assert "G1->G" in result["target_entities"][0]  # Corrected check


def test_predictive_buffer_capacity_threshold(agent):
    """Test PREDICTIVE_BUFFER trigger at >90% capacity."""
    # S1 max capacity is 12000. 10801 is > 90%.
    state = StadiumState(occupancy={"S1": 10801}, wait_times={})
    result = json.loads(agent.evaluate_plays(state))

    assert result["action_type"] == "PREDICTIVE_BUFFER"
    assert "S1" in result["target_entities"]
