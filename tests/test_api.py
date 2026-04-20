"""
StadiumPulse API Integration Tests.

This module validates the RESTful interface of the orchestration cluster,
ensuring security enforcement and correct data serialization.
"""

from fastapi.testclient import TestClient
from src.api.server import app, STADIUM_API_KEY

client = TestClient(app)

# --- Common Test Data ---
VALID_HEADERS = {"X-API-Key": STADIUM_API_KEY}
INVALID_HEADERS = {"X-API-Key": "wrong-secret"}


def test_api_root():
    """Verifies that the root health check is accessible without auth."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_unauthorized_access():
    """Ensures that protected endpoints reject requests without a valid API key."""
    endpoints = [
        ("GET", "/stadium/state"),
        ("POST", "/stadium/update"),
        ("GET", "/optimizer/decision"),
        ("POST", "/simulation/run"),
    ]
    for method, path in endpoints:
        if method == "GET":
            response = client.get(path, headers=INVALID_HEADERS)
        else:
            response = client.post(path, headers=INVALID_HEADERS, json={})

        assert response.status_code == 403
        assert response.json()["detail"] == "Could not validate API Key"


def test_get_stadium_state():
    """Verifies retrieval of current stadium metrics."""
    response = client.get("/stadium/state", headers=VALID_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "occupancy" in data
    assert "wait_times" in data


def test_post_stadium_update():
    """Tests the synchronization of external sensor data."""
    update_payload = {"occupancy": {"S1": 5000}, "wait_times": {"G1": 10.5}}
    response = client.post("/stadium/update", headers=VALID_HEADERS, json=update_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_get_optimizer_decision():
    """Verifies the AI reasoning and strategy endpoint."""
    response = client.get("/optimizer/decision", headers=VALID_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "action_type" in data
    assert "reasoning_trace" in data
    assert isinstance(data["reasoning_trace"], list)


def test_run_simulation_scenario():
    """Tests the remote execution of synthetic chaos scenarios."""
    scenarios = ["nominal", "gate_spike", "concession_spike"]
    for scenario in scenarios:
        payload = {"scenario_type": scenario, "severity": 1}
        response = client.post("/simulation/run", headers=VALID_HEADERS, json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "simulation_triggered"
        assert response.json()["scenario"] == scenario


def test_simulation_invalid_type():
    """Ensures the simulation engine rejects unsupported scenario types."""
    payload = {"scenario_type": "alien_invasion", "severity": 99}
    response = client.post("/simulation/run", headers=VALID_HEADERS, json=payload)
    assert response.status_code == 400
    assert "Unsupported scenario type" in response.json()["detail"]
