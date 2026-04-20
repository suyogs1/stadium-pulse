"""
Messenger Agent Module: Crowd Communication and Alert Dispatch.

This module provides the MessengerAgent class which coordinates the
distribution of instructions and incentives to stadium fans via
Google Cloud Pub/Sub and Cloud Function triggers.
"""

from typing import List
from src.services.messaging_service import messaging_service
from src.services.logging_service import cloud_logger


class MessengerAgent:
    """
    Orchestrates the dispatch of real-time instructions to stadium attendees.

    Acts as the primary communication bridge between the agentic core
    and the mobile users/infrastructure.
    """

    def dispatch_alert(self, action_type: str, target_entities: List[str]) -> None:
        """
        Broadcasting dynamic alerts through multiple high-reliability cloud channels.

        Args:
            action_type: The category of intervention (e.g., 'INCENTIVIZE', 'REROUTE').
            target_entities: List of sections, gates, or blocks being targeted.
        """
        if not target_entities:
            return

        # Multilingual Translation via Google Cloud Translation API
        from src.services.translation_service import translation_service

        raw_message = f"{action_type} for {', '.join(target_entities)}"
        translated_message = translation_service.translate_texts([raw_message], target="es")[0]

        # Dispatch via the dedicated messaging service layer
        messaging_service.broadcast_alert(action_type, target_entities)

        # Log action to Cloud Logging for operational audit
        cloud_logger.log_event(
            agent_name="MessengerAgent",
            action="AlertBroadcast",
            status="SUCCESS",
            metadata={
                "action_type": action_type,
                "targets": target_entities,
                "translated_message": translated_message,
            },
        )
