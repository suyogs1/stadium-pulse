"""
Messenger Agent: Crowd Communication and Alert Dispatch.

This module handles the distribution of instructions and incentives 
to fans via Google Cloud Pub/Sub and Cloud Function triggers.
"""

import time
from typing import List, Dict, Any, Optional
from services.google_services import messenger_service, pubsub_publisher

class MessengerAgent:
    """
    Orchestrates the dispatch of real-time instructions to stadium attendees.
    """
    
    def dispatch_alert(self, action_type: str, target_entities: List[str]) -> Optional[Dict[str, Any]]:
        """
        Broadcasting dynamic alerts through multiple high-reliability cloud channels.
        
        Args:
            action_type: The category of intervention (e.g., 'INCENTIVIZE', 'REROUTE').
            target_entities: List of sections, gates, or blocks being targeted.
            
        Returns:
            The execution trace from the primary messenger service if successful.
        """
        if not target_entities:
            return None
            
        # Strategy-aware message generation
        if action_type == "INCENTIVIZE":
            message = f"Exclusive 20% Discount! Visit concessions: {', '.join(target_entities)} to avoid queues."
        elif action_type == "REROUTE":
            message = f"Alert: Please use alternative gates {', '.join(target_entities)} for faster entry."
        else:
            message = f"Stadium Update: {action_type} in progress for {', '.join(target_entities)}."
            
        alert_payload = {
            "message": message,
            "action_type": action_type,
            "target_entities": target_entities,
            "timestamp": str(time.time())
        }
        
        # Dual-dispatch pattern for high reliability (Google Services Best Practice)
        # 1. Background persistence and analysis
        pubsub_publisher.publish_alert(alert_payload)
        
        # 2. Immediate push notification delivery
        return messenger_service.trigger_push_notification(alert_payload)
