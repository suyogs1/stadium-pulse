import pytest
import json
from src.agents.pulse_agent import PulseAgent
from src.core.models import StadiumState


@pytest.fixture
def state_file(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    f = d / "state.json"
    return str(f)


def test_pulse_cold_start(state_file):
    """Test behavior when the state file does not exist yet."""
    agent = PulseAgent(state_file)
    state = agent.scan_stadium_state()
    assert isinstance(state, StadiumState)
    assert len(state.occupancy) == 0


def test_pulse_scan_valid_file(state_file):
    """Test scanning a valid JSON state file."""
    data = {"occupancy": {"S1": 5000}, "wait_times": {"G1": 10.0}}
    with open(state_file, "w") as f:
        json.dump(data, f)

    agent = PulseAgent(state_file)
    state = agent.scan_stadium_state()
    assert state.occupancy["S1"] == 5000
    assert state.wait_times["G1"] == 10.0


def test_anomaly_detection():
    """Test anomaly detection logic against historical benchmarks."""
    agent = PulseAgent("mock.json")
    current_state = StadiumState(occupancy={"S1": 12000, "S2": 1000}, wait_times={})

    # S1: 12000/13000 ~ 0.92
    # S2: 1000/13000 ~ 0.07

    baseline = {
        "S1": 0.5,  # Huge variance (0.92 - 0.5 = 0.42 > 0.3)
        "S2": 0.1,  # Nominal variance (0.07 - 0.1 = 0.03 < 0.3)
    }

    anomalies = agent.detect_anomalies(current_state, baseline)
    assert "S1" in anomalies
    assert "S2" not in anomalies


def test_anomaly_detection_full_stadium():
    """Test scanning all 10 sections for anomalies."""
    agent = PulseAgent("mock.json")
    current_occupancy = {f"S{i}": 13000 if i % 2 == 0 else 1000 for i in range(1, 11)}
    current_state = StadiumState(occupancy=current_occupancy, wait_times={})

    # Baseline is exactly 50% for everyone
    baseline = {f"S{i}": 0.5 for i in range(1, 11)}

    # Sections 2, 4, 6, 8, 10 are at 100% (diff 0.5 > 0.3) -> Anomalies
    # Sections 1, 3, 5, 7, 9 are at ~7% (diff 0.43 > 0.3) -> Anomalies
    # Wait, 1000/13000 = 0.076. 0.5 - 0.076 = 0.424 > 0.3.
    # So all sections should be anomalies in this extreme case.

    anomalies = agent.detect_anomalies(current_state, baseline)
    assert len(anomalies) == 10
