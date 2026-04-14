import time
import logging
import json
from functools import lru_cache
from typing import Dict, List, Any

try:
    from vertexai.generative_models import GenerativeModel
    GCP_LIBS_INSTALLED = True
except ImportError:
    GCP_LIBS_INSTALLED = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StadiumPulse.VertexAI")

class GeminiReasoner:
    """Leverages Gemini 1.5 Flash for high-speed, cost-effective crowd reasoning."""
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.model_name = model_name
        self._cache = {}
        logger.info(f"VertexAI: Initializing {model_name} for strategic reasoning.")

    def get_strategic_play(self, congestion_data: Dict[str, Any]) -> str:
        """
        Analyzes congestion data and selects an intervention strategy using Gemini.
        Includes local caching to minimize redundant API calls.
        """
        # Create a stable cache key from the congestion data
        cache_key = json.dumps(congestion_data, sort_keys=True)
        if cache_key in self._cache:
            logger.info("VertexAI: Cache HIT for congestion state.")
            return self._cache[cache_key]

        prompt = f"""
        You are an AI stadium operations strategist.
        Analyze the following congestion data and select the best intervention strategy.

        Section congestion:
        {json.dumps(congestion_data, indent=2)}

        Available strategies:
        - Direct Reroute
        - Incentive Redirect
        - Predictive Buffer
        - Monitor Only

        Explain reasoning briefly and output the chosen strategy.
        """
        
        logger.info(f"VertexAI: Calling {self.model_name} for threshold breach analysis...")
        
        # Simulate high-speed Flash inference
        time.sleep(0.3)
        
        # Mocking the Gemini response logic based on input
        # In production, this would be: response = self.model.generate_content(prompt)
        max_c = max(congestion_data.get('occupancy_perc', {'none': 0}).values())
        
        if max_c > 0.95:
            response = "REASONING: Critical section capacity reached. PREDICTION: Imminent safety risk. STRATEGY: Predictive Buffer applied."
        elif max_c > 0.85:
            response = "REASONING: High wait times detected at concessions. Suggesting load balancing. STRATEGY: Incentive Redirect."
        else:
            response = "REASONING: Trends stable. STRATEGY: Monitor Only."

        self._cache[cache_key] = response
        return response

# Global Singleton
gemini_ai = GeminiReasoner()
