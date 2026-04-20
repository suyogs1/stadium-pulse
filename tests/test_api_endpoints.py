"""
StadiumPulse API Endpoint Testing Suite.

Verifies the correctness of the FastAPI interface, including
authentication, serialization, and error handling.
"""

from fastapi.testclient import TestClient
from src.api.server import app, STADIUM_API_KEY

client = TestClient(app)
VALID_HEADERS = {"X-API-Key": STADIUM_API_KEY}


def test_stadium_state_endpoint():
    """Verify that /stadium/state returns valid venue telemetry."""
    response = client.get("/stadium/state", headers=VALID_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "occupancy" in data
    assert "wait_times" in data
    assert isinstance(data["occupancy"], dict)


def test_stadium_update_endpoint():
    """Verify that /stadium/update correctly persists new sensor data."""
    payload = {"occupancy": {"S1": 7500, "S2": 11000}, "wait_times": {"G1": 12.0}}
    response = client.post("/stadium/update", headers=VALID_HEADERS, json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_optimizer_decision_endpoint():
    """Verify that /optimizer/decision exposes AI Reasoning metadata."""
    response = client.get("/optimizer/decision", headers=VALID_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "action_type" in data
    assert "is_ai_decision" in data  # New field verification
    assert "reasoning_trace" in data


def test_simulation_run_endpoint_scenarios():
    """Verify that /simulation/run supports various operational scenarios."""
    for scenario in ["nominal", "gate_spike"]:
        payload = {"scenario_type": scenario, "severity": 2}
        response = client.post("/simulation/run", headers=VALID_HEADERS, json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "simulation_triggered"


def test_endpoint_authentication_enforcement():
    """Verify that restricted endpoints reject missing or invalid credentials."""
    invalid_headers = {"X-API-Key": "invalid-token-403"}
    response = client.get("/stadium/state", headers=invalid_headers)
    assert response.status_code == 403
    assert "validate API Key" in response.json()["detail"]


def test_simulation_invalid_input_rejection():
    """Verify that the API correctly identifies and rejects malformed simulation requests."""
    payload = {"scenario_type": "invalid_mode", "severity": 0}
    response = client.post("/simulation/run", headers=VALID_HEADERS, json=payload)
    assert response.status_code == 400
    assert "Unsupported scenario type" in response.json()["detail"]
