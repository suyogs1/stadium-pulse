"""
StadiumPulse Performance & Latency Validation.

Ensures that core agentic orchestration and simulation loops 
operate within strict timing thresholds necessary for real-time response.
"""

import time
import pytest
from config import NARENDRA_MODI_STADIUM
from src.simulation.scenario_engine import ScenarioEngine
from src.agents.optimizer_agent import OptimizerAgent

# --- Threshold Definitions (Seconds) ---
MAX_SIMULATION_LATENCY = 0.5   # Simulation generation should be near instantaneous
MAX_OPTIMIZER_LATENCY = 3.0    # Reasoner including AI logic should remain fast
MAX_HEURISTIC_LATENCY = 0.5    # Local rule-based checks must be sub-second

@pytest.fixture
def perf_context():
    """Provides the necessary engine and agent cluster for timing tests."""
    engine = ScenarioEngine(NARENDRA_MODI_STADIUM)
    optimizer = OptimizerAgent(NARENDRA_MODI_STADIUM)
    return engine, optimizer

def test_simulation_engine_latency(perf_context):
    """Verifies that synthetic data generation is high-performance."""
    engine, _ = perf_context
    
    start_time = time.time()
    for _ in range(10): # Average over 10 runs
        engine.generate_nominal_state()
    duration = (time.time() - start_time) / 10
    
    print(f"DEBUG: Avg Simulation Latency: {duration:.4f}s")
    assert duration < MAX_SIMULATION_LATENCY, f"Simulation engine too slow: {duration:.4f}s"

def test_optimizer_heuristic_latency(perf_context):
    """
    Measures the latency of the Optimizer's heuristic decision tree.
    (Testing nominal state to avoid triggering Gemini during this test).
    """
    engine, optimizer = perf_context
    nominal_state = engine.generate_nominal_state()
    
    start_time = time.time()
    optimizer.evaluate_plays(nominal_state)
    duration = time.time() - start_time
    
    print(f"DEBUG: Heuristic Decision Latency: {duration:.4f}s")
    assert duration < MAX_HEURISTIC_LATENCY, f"Heuristic optimizer too slow: {duration:.4f}s"

def test_scenario_injection_latency(perf_context):
    """Ensures that complex congestion spikes can be injected rapidly."""
    engine, _ = perf_context
    state = engine.generate_nominal_state()
    
    start_time = time.time()
    engine.inject_congestion_spike(state, "gate", severity_count=3)
    duration = time.time() - start_time
    
    print(f"DEBUG: Scenario Injection Latency: {duration:.4f}s")
    assert duration < MAX_SIMULATION_LATENCY, f"Scenario injection too slow: {duration:.4f}s"

def test_high_load_optimizer_latency(perf_context):
    """
    Measures orchestration latency under high load (triggering agentic logic).
    Note: In simulation mode, this should still be well within the threshold.
    """
    engine, optimizer = perf_context
    
    # Generate an overcrowded state to trigger full reasoning
    state = engine.generate_nominal_state()
    for section in NARENDRA_MODI_STADIUM.sections:
        state.occupancy[section.section_id] = int(section.capacity * 0.95)
        
    start_time = time.time()
    optimizer.evaluate_plays(state)
    duration = time.time() - start_time
    
    print(f"DEBUG: High-Load Orchestration Latency: {duration:.4f}s")
    assert duration < MAX_OPTIMIZER_LATENCY, f"AI-Driven optimizer too slow: {duration:.4f}s"
