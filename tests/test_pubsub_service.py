"""
Unit Tests for PubSubService.

Ensures that event serialization and publishing pathways are
correctly verified, focusing on both mock and fallback modes.
"""

from unittest.mock import MagicMock, patch
from src.services.pubsub_service import PubSubService


def test_event_serialization():
    """Verify that congestion events are correctly serialized for Pub/Sub."""
    service = PubSubService(project_id="test-proj")
    # Test with simulated lack of publisher
    event_id = service.publish_congestion_event("S1", 5000, 10000)

    assert event_id.startswith("EVT-")
    # Even if publisher is missing, it should log and return ID
    assert len(event_id) > 8


@patch("src.services.pubsub_service.pubsub_v1", create=True)
@patch("src.services.pubsub_service.GCP_AVAILABLE", True)
@patch("src.services.pubsub_service.settings")
def test_publisher_engagement(mock_settings, mock_pubsub):
    """Verify that the real publisher is called when GCP is available."""
    mock_settings.ENABLE_PUBSUB_PIPELINE = True
    mock_settings.GOOGLE_PROJECT_ID = "active-proj"

    mock_pub_instance = MagicMock()
    mock_pubsub.PublisherClient.return_value = mock_pub_instance

    service = PubSubService(project_id="active-proj")
    assert service.publisher is not None

    service.publish_congestion_event("S1", 1000, 5000)
    mock_pub_instance.publish.assert_called_once()


def test_subscribe_init():
    """Verify subscription entry point."""
    service = PubSubService()
    service.subscribe_to_telemetry(lambda x: None)
    # Checks pass if no exception
