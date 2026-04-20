"""
Pub/Sub Event Service: real-time Pipeline Orchestration.

Manages the ingestion and distribution of stadium congestion events
via Google Cloud Pub/Sub, enabling a decoupled, event-driven architecture.
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from src.core.settings import settings

try:
    from google.cloud import pubsub_v1
    from types import SimpleNamespace

    GCP_AVAILABLE: bool = True
except ImportError:
    GCP_AVAILABLE = False
    from types import SimpleNamespace

    pubsub_v1 = SimpleNamespace()

pubsub_logger: logging.Logger = logging.getLogger("StadiumPulse.PubSubService")


class PubSubService:
    """
    Client for high-throughput event streaming within the stadium ecosystem.
    """

    def __init__(self, project_id: str = settings.GOOGLE_PROJECT_ID) -> None:
        """Initializes the Pub/Sub clients."""
        self.project_id: str = project_id
        self.topic_id: str = "stadium-telemetry"
        self.subscription_id: str = "stadium-optimizer-sub"
        self.publisher: Optional[pubsub_v1.PublisherClient] = None
        self.subscriber: Optional[pubsub_v1.SubscriberClient] = None
        self._callbacks: List[Callable] = []

        if GCP_AVAILABLE and settings.ENABLE_PUBSUB_PIPELINE:
            try:
                self.publisher = pubsub_v1.PublisherClient()
                self.subscriber = pubsub_v1.SubscriberClient()
                pubsub_logger.info("PubSub: Publisher and Subscriber clients initialized.")
            except Exception as e:
                pubsub_logger.warning(
                    "PubSub: Initialization failed (%s). Fallback mode active.", e
                )

    def publish_congestion_event(self, section_id: str, occupancy: int, capacity: int) -> str:
        """
        Publishes a raw congestion signal to the 'stadium-telemetry' topic.

        Args:
            section_id: Identity of the seating sector.
            occupancy: Current headcount.
            capacity: Max capacity of the sector.

        Returns:
            The generated event_id for tracking.
        """
        event_id: str = f"EVT-{uuid.uuid4().hex[:8].upper()}"
        payload: Dict[str, Any] = {
            "event_id": event_id,
            "section_id": section_id,
            "congestion_level": round(occupancy / capacity, 4),
            "timestamp": datetime.now().isoformat(),
        }

        message_data: bytes = json.dumps(payload).encode("utf-8")

        if self.publisher:
            topic_path = self.publisher.topic_path(self.project_id, self.topic_id)
            try:
                self.publisher.publish(topic_path, message_data)
                pubsub_logger.info(
                    "PubSub-Live: Event %s published to %s.", event_id, self.topic_id
                )
            except Exception as e:
                pubsub_logger.error("PubSub-Live: Publish failed for %s: %s", event_id, e)
        else:
            # SHIM: In mock mode, we manually trigger the registered callbacks
            # to simulate the decoupled architecture locally.
            for cb in self._callbacks:
                cb(payload)

        pubsub_logger.info(
            "[EVENT-PUSH] ID: %s | Section: %s | Load: %.2f",
            event_id,
            section_id,
            payload["congestion_level"],
        )
        return event_id

    def subscribe_to_telemetry(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Registers a callback to process incoming telemetry events.
        """
        if self.subscriber:
            subscription_path = self.subscriber.subscription_path(
                self.project_id, self.subscription_id
            )

            def wrapped_callback(message: Any) -> None:
                try:
                    data = json.loads(message.data.decode("utf-8"))
                    callback(data)
                    message.ack()
                except Exception as e:
                    pubsub_logger.error("PubSub: Callback error: %s", e)
                    message.nack()

            self.subscriber.subscribe(subscription_path, callback=wrapped_callback)
            pubsub_logger.info("PubSub-Live: Streaming active on %s.", self.subscription_id)
        else:
            self._callbacks.append(callback)
            pubsub_logger.info("PubSub-Mock: Listener registered (Fallback mode).")


# GLOBAL SERVICE INSTANCE
pubsub_service: PubSubService = PubSubService()
