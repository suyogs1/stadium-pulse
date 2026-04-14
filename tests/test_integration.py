import pytest
import asyncio
import json
from unittest.mock import patch, MagicMock
from src.main import StadiumPulseApp
from config import StadiumState

@pytest.fixture
def app(tmp_path):
    f = tmp_path / "stadium_state.json"
    f.write_text(json.dumps({"occupancy": {"S1": 13000}, "wait_times": {"G1": 20.0}}))
    app_instance = StadiumPulseApp()
    app_instance.state_file = str(f)
    app_instance.pulse.state_file_path = str(f)
    return app_instance

@pytest.mark.asyncio
@patch('src.main.bq_client')
@patch('src.agents.messenger_agent.pubsub_publisher')
@patch('src.agents.messenger_agent.messenger_service')
async def test_full_simulation_chaos_to_calm(mock_service, mock_pubsub, mock_bq, app):
    mock_bq.fetch_historical_averages.return_value = {f"S{i}": 0.5 for i in range(1, 11)}
    with patch('asyncio.sleep', return_value=None):
        await app.run_simulation()
    assert mock_bq.fetch_historical_averages.called
    assert mock_pubsub.publish_alert.called

@pytest.mark.asyncio
@patch('src.main.bq_client')
@patch('src.agents.messenger_agent.pubsub_publisher')
@patch('src.agents.messenger_agent.messenger_service')
async def test_integration_nominal_success(mock_service, mock_pubsub, mock_bq, app):
    with open(app.state_file, 'w') as f:
        json.dump({"occupancy": {"S1": 5000}, "wait_times": {"G1": 5.0}}, f)
    mock_bq.fetch_historical_averages.return_value = {"S1": 0.4}
    with patch('asyncio.sleep', return_value=None):
        await app.run_simulation()
    assert not mock_pubsub.publish_alert.called
