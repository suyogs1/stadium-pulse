import pytest
import json
from unittest.mock import patch
from src.main import StadiumPulseSimulationApp


@pytest.fixture
def app(tmp_path):
    f = tmp_path / "stadium_state.json"
    f.write_text(json.dumps({"occupancy": {"S1": 13000}, "wait_times": {"G1": 20.0}}))
    app_instance = StadiumPulseSimulationApp()
    app_instance.state_file_path = str(f)
    app_instance.pulse_agent.state_file_path = str(f)
    return app_instance


@pytest.mark.asyncio
@patch("src.main.bq_service")
@patch("src.agents.messenger_agent.messaging_service")
async def test_full_simulation_chaos_to_calm(mock_msg_service, mock_bq, app):
    """Verify that a full simulation pass correctly interacts with services when under stress."""
    mock_bq.get_historical_baseline.return_value = {f"S{i}": 0.5 for i in range(1, 11)}

    with patch("asyncio.sleep", return_value=None):
        await app.execute_simulation_pass()

    assert mock_bq.get_historical_baseline.called
    assert mock_msg_service.broadcast_alert.called


@pytest.mark.asyncio
@patch("src.main.bq_service")
@patch("src.agents.messenger_agent.messaging_service")
async def test_integration_nominal_success(mock_msg_service, mock_bq, app):
    """Verify that nominal conditions do not trigger unnecessary alerts."""
    with open(app.state_file_path, "w") as f:
        json.dump({"occupancy": {"S1": 5000}, "wait_times": {"G1": 5.0}}, f)

    mock_bq.get_historical_baseline.return_value = {f"S{i}": 0.5 for i in range(1, 11)}

    with patch("asyncio.sleep", return_value=None):
        await app.execute_simulation_pass()

    # In nominal state, no alerts should be broadcasted
    assert not mock_msg_service.broadcast_alert.called
