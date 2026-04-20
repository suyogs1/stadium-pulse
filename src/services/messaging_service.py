"""
Messaging Service: Real-time Alerting and Notification.

Coordinates fan communication via Pub/Sub broadcasting and
Google Cloud Function triggers.
"""

import logging
from typing import List
from src.services.logging_service import cloud_logger

msg_service_logger: logging.Logger = logging.getLogger("StadiumPulse.MessagingService")


class MessagingService:
    """
    Client for high-velocity message delivery to fans.
    """

    def broadcast_alert(self, action: str, targets: List[str]) -> None:
        """
        Dispatches a strategic alert to the targeted crowd segments.
        """
        message: str = self._generate_message(action, targets)

        msg_service_logger.info("[MESSENGER] Dispatching: %s", message)

        # 1. Pub/Sub Broadcast (Mocked)
        msg_service_logger.info("PubSub: Alert enqueued for global topic.")

        # 2. Audit Log
        cloud_logger.log_event(
            agent_name="MessagingService",
            action="Broadcast",
            status="SENT",
            metadata={"msg": message, "targets": targets},
        )

        # 3. GCF Push Trigger (Mocked)
        msg_service_logger.info("CloudFunction: Triggering mobile-push-service cluster.")

    def _generate_message(self, action: str, targets: List[str]) -> str:
        """Determines the exact instruction text for the fans."""
        if action == "INCENTIVIZE":
            return f"Special Offer! Visit stands in {', '.join(targets)} for 20% off."
        if action == "REROUTE":
            return f"Attention: Please use Gates {', '.join(targets)} to avoid congestion."
        return f"Operational update for sectors {', '.join(targets)}."


# GLOBAL SERVICE INSTANCE
messaging_service: MessagingService = MessagingService()
