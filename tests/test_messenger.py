import pytest
from unittest.mock import patch, MagicMock
from src.agents.messenger_agent import MessengerAgent
import time

@pytest.fixture
def messenger():
    return MessengerAgent()

@patch('src.agents.messenger_agent.pubsub_publisher')
@patch('src.agents.messenger_agent.messenger_service')
def test_dispatch_incentive_tone(mock_service, mock_pubsub, messenger):
    """Validate tone for INCENTIVIZE action."""
    messenger.dispatch_alert("INCENTIVIZE", ["C1", "C2"])
    
    # Check PubSub call
    assert mock_pubsub.publish_alert.called
    args, _ = mock_pubsub.publish_alert.call_args
    payload = args[0]
    
    assert "20% Discount" in payload["message"]
    assert "C1, C2" in payload["message"]
    assert payload["action_type"] == "INCENTIVIZE"

@patch('src.agents.messenger_agent.pubsub_publisher')
@patch('src.agents.messenger_agent.messenger_service')
def test_dispatch_urgency_tone(mock_service, mock_pubsub, messenger):
    """Validate tone for REROUTE action (Urgency)."""
    messenger.dispatch_alert("REROUTE", ["G1->G2"])
    
    args, _ = mock_pubsub.publish_alert.call_args
    payload = args[0]
    
    assert "Alert:" in payload["message"]
    assert "faster entry" in payload["message"]
    assert payload["action_type"] == "REROUTE"

@patch('src.agents.messenger_agent.pubsub_publisher')
@patch('src.agents.messenger_agent.messenger_service')
def test_dispatch_empty_entities(mock_service, mock_pubsub, messenger):
    """Ensure no notification is sent if no entities are targeted."""
    messenger.dispatch_alert("INCENTIVIZE", [])
    
    assert not mock_pubsub.publish_alert.called
    assert not mock_service.trigger_push_notification.called

@patch('src.agents.messenger_agent.pubsub_publisher')
@patch('src.agents.messenger_agent.messenger_service')
def test_messenger_timestamp(mock_service, mock_pubsub, messenger):
    """Verify timestamp is included in the payload."""
    messenger.dispatch_alert("MONITOR_ONLY", ["S1"])
    
    args, _ = mock_pubsub.publish_alert.call_args
    payload = args[0]
    assert "timestamp" in payload
