import pytest
from src.simulation.scenario_engine import ScenarioEngine
from config import NARENDRA_MODI_STADIUM, StadiumState

def test_engine_nominal_state():
    """Verify standard state generation."""
    engine = ScenarioEngine(NARENDRA_MODI_STADIUM)
    state = engine.generate_nominal_state()
    
    assert isinstance(state, StadiumState)
    assert len(state.occupancy) == 10
    # Check bounds (random.uniform(0.4, 0.6) of capacity)
    for section in NARENDRA_MODI_STADIUM.sections:
        occ = state.occupancy[section.section_id]
        assert occ >= int(section.capacity * 0.39) and occ <= int(section.capacity * 0.61)

def test_engine_spike_injection():
    """Verify targeted congestion spikes."""
    engine = ScenarioEngine(NARENDRA_MODI_STADIUM)
    state = engine.generate_nominal_state()
    
    # Inject concession spike
    spiked_state = engine.inject_congestion_spike(state, "concession", severity_count=1)
    high_waits = [v for v in spiked_state.wait_times.values() if v >= 15.0]
    assert len(high_waits) >= 1

    # Inject gate spike
    gate_state = engine.inject_congestion_spike(state, "gate", severity_count=1)
    high_gate_waits = [v for v in gate_state.wait_times.values() if v >= 20.0]
    assert len(high_gate_waits) >= 1

def test_simulation_progression():
    """Verify specific timeline steps."""
    engine = ScenarioEngine(NARENDRA_MODI_STADIUM)
    
    # Minute 2 should have a spike
    state_m2 = engine.simulate_simulation_step(2)
    high_waits = [v for v in state_m2.wait_times.values() if v >= 15.0]
    assert len(high_waits) >= 1
    
    # Minute 4 should be normalizing
    state_m4 = engine.simulate_simulation_step(4)
    # Verification method runs
    assert isinstance(state_m4, StadiumState)
