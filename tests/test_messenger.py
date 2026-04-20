import pytest
from unittest.mock import patch
from src.agents.messenger_agent import MessengerAgent


@pytest.fixture
def messenger():
    return MessengerAgent()


@patch("src.agents.messenger_agent.messaging_service")
def test_dispatch_incentive_broadcasting(mock_msg_service, messenger):
    """Validate that incentives are correctly broadcasted via the services layer."""
    messenger.dispatch_alert("INCENTIVIZE", ["C1", "C2"])

    # Verify MessagingService was engaged
    mock_msg_service.broadcast_alert.assert_called_once()
    args, _ = mock_msg_service.broadcast_alert.call_args
    assert args[0] == "INCENTIVIZE"
    assert "C1" in args[1]


@patch("src.agents.messenger_agent.messaging_service")
def test_dispatch_reroute_broadcasting(mock_msg_service, messenger):
    """Validate that reroute alerts are correctly broadcasted."""
    messenger.dispatch_alert("REROUTE", ["G1->G2"])

    mock_msg_service.broadcast_alert.assert_called_once()
    args, _ = mock_msg_service.broadcast_alert.call_args
    assert args[0] == "REROUTE"
    assert "G1->G2" in args[1]


@patch("src.agents.messenger_agent.messaging_service")
def test_dispatch_empty_entities(mock_msg_service, messenger):
    """Ensure no notification is sent if no entities are targeted unless MONITOR_ONLY."""
    messenger.dispatch_alert("INCENTIVIZE", [])

    # Should skip broadcasting for empty entity lists on active actions
    assert not mock_msg_service.broadcast_alert.called


@patch("src.agents.messenger_agent.cloud_logger")
def test_messenger_logging_integration(mock_logger, messenger):
    """Verify that the MessengerAgent correctly audits its actions to the cloud logger."""
    with patch("src.agents.messenger_agent.messaging_service"):
        messenger.dispatch_alert("INCENTIVIZE", ["C1"])

    mock_logger.log_event.assert_called_once()
    assert mock_logger.log_event.call_args[1]["agent_name"] == "MessengerAgent"
