import time
from services.google_services import messenger_service, pubsub_publisher

class MessengerAgent:
    """Agent responsible for communicating with fans via Google Cloud services."""
    
    def dispatch_alert(self, action_type: str, target_entities: list):
        """Dispatches dynamic alerts via Google Cloud Pub/Sub and Cloud Functions."""
        if not target_entities:
            return
            
        message = f"Stadium Update: {action_type} in progress for {', '.join(target_entities)}."
        if action_type == "INCENTIVIZE":
            message = f"Exclusive 20% Discount! Visit concessions: {', '.join(target_entities)} to avoid queues."
        elif action_type == "REROUTE":
            message = f"Alert: Please use alternative gates {', '.join(target_entities)} for faster entry."
            
        payload = {
            "message": message,
            "action_type": action_type,
            "target_entities": target_entities,
            "timestamp": str(time.time())
        }
        
        # Dual-dispatch pattern for high reliability (Google Services Best Practice)
        pubsub_publisher.publish_alert(payload)
        return messenger_service.trigger_push_notification(payload)
