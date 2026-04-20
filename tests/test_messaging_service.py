"""
Unit Tests for MessagingService.

Ensures that message generation and service dispatch logic
are correctly verified with real instances.
"""

from src.services.messaging_service import MessagingService
from unittest.mock import patch


def test_message_generation():
    """Verify that instructions are correctly generated for various actions."""
    service = MessagingService()

    msg_inc = service._generate_message("INCENTIVIZE", ["S1", "S2"])
    assert "20% off" in msg_inc
    assert "S1, S2" in msg_inc

    msg_rer = service._generate_message("REROUTE", ["G1->G2"])
    assert "use Gates G1->G2" in msg_rer

    msg_def = service._generate_message("UNKNOWN", ["X1"])
    assert "Operational update" in msg_def


@patch("src.services.messaging_service.cloud_logger")
def test_broadcast_alert_flow(mock_logger):
    """Verify that broadcast_alert executes its logical steps and logs the outcome."""
    service = MessagingService()
    service.broadcast_alert("INCENTIVIZE", ["S1"])

    mock_logger.log_event.assert_called_once()
    args, kwargs = mock_logger.log_event.call_args
    assert kwargs["agent_name"] == "MessagingService"
    assert "20% off" in kwargs["metadata"]["msg"]
