import pytest
from src.services.google_services import bq_client, pubsub_publisher, messenger_service
from src.services.gemini_reasoner import gemini_ai

def test_bq_fetch_mock():
    """Verify mock BigQuery results."""
    res = bq_client.fetch_historical_averages(10)
    assert len(res) == 10
    assert "S1" in res

def test_vertex_ai_prediction():
    """Verify VertexAI mock prediction logic."""
    res = gemini_ai.get_strategic_play({"occupancy_perc": {"S1": 1.0}})
    assert "STRATEGY:" in res

def test_pubsub_publish():
    """Verify PubSub mock publishing."""
    res = pubsub_publisher.publish_alert({"action": "test"})
    assert "message_id" in res

def test_gcf_trigger():
    """Verify GCF mock trigger."""
    res = messenger_service.trigger_push_notification({"msg": "hi"})
    assert res["status"] == "success"
