"""
Gemini Reasoner Service: Advanced AI Logic for Crowd Management.

This module provides a wrapper for the Gemini 1.5 Flash model 
to perform complex strategic analysis on stadium congestion data.
"""

import time
import logging
import json
import os
from typing import Dict, List, Any, Optional

# Import the Google Generative AI SDK
try:
    import google.generativeai as genai
    GENAI_SDK_INSTALLED = True
except ImportError:
    GENAI_SDK_INSTALLED = False

from config import GEMINI_API_KEY

# Configure logging for AI operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StadiumPulse.GeminiAI")

class GeminiReasoner:
    """
    Leverages Gemini 1.5 Flash for high-speed, cost-effective crowd reasoning.
    Supports both Google AI API and mock-mode for development and CI.
    """
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """
        Initializes the Gemini reasoner. 
        Configures the SDK if a valid API key is present in the environment.
        """
        self.model_name = model_name
        self._execution_cache: Dict[str, str] = {}
        self.api_active = False
        
        if GENAI_SDK_INSTALLED and GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel(model_name)
                self.api_active = True
                logger.info(f"GeminiAI: SDK configured successfully with {model_name}.")
            except Exception as e:
                logger.error(f"GeminiAI: Configuration failed. Error: {e}")
        else:
            if not GENAI_SDK_INSTALLED:
                logger.warning("GeminiAI: google-generativeai SDK not found. Running in SIMULATION mode.")
            if not GEMINI_API_KEY:
                logger.info("GeminiAI: No GEMINI_API_KEY detected. Running in SIMULATION mode.")

    def get_strategic_play(self, context_data: Dict[str, Any]) -> str:
        """
        Analyzes venue congestion metrics and suggests an optimal intervention.
        
        Args:
            context_data: Mapping containing occupancy percentages, wait times, 
                         neighbors, and walking distances.
            
        Returns:
            A string containing the AI's reasoning and the suggested strategy.
        """
        # Generate a stable cache key to minimize API usage
        state_signature = json.dumps(context_data, sort_keys=True)
        if state_signature in self._execution_cache:
            logger.info("GeminiAI: Cache HIT. Returning stored reasoning.")
            return self._execution_cache[state_signature]

        # Strategic Prompt Construction
        system_prompt = f"""
        You are an Expert Stadium Operations Strategist.
        Task: Analyze the provided congestion data and select the absolute best intervention strategy.

        Input Context Data:
        {json.dumps(context_data, indent=2)}

        Analysis Requirements:
        1. Identify the most congested sections (Primary Bottlenecks).
        2. Evaluate "Nearby Sections": Check their current spare capacity.
        3. Consider "Walking Distance": Is a redirect feasible based on the distance (meters)?
        4. Cross-reference with Gate/Concession wait times.

        Intervention Strategies:
        - Direct Reroute: Physically moving fans from congested sectors to empty ones.
        - Incentive Redirect: Using mobile discounts to pull fans toward under-utilized blocks.
        - Predictive Buffer: Slowing down ingress/egress to prevent a safety incident.
        - Monitor Only: No action required; metrics are within safe limits.

        Output Format:
        REASONING: [Brief explanation of bottleneck and nearby capacity evaluation]
        STRATEGY: [One of the 4 strategies listed above]
        """
        
        logger.info(f"GeminiAI: Requesting reasoning from {self.model_name}...")
        
        try:
            if self.api_active:
                # Real API Call using Google Generative AI SDK
                response = self.model.generate_content(system_prompt)
                analysis = response.text.strip()
            else:
                # Intelligent Fallback Logic for Simulation Mode
                time.sleep(0.5)
                analysis = self._generate_fallback_response(context_data)
        except Exception as e:
            logger.error(f"GeminiAI: API Execution Error. Falling back. Error: {e}")
            analysis = self._generate_fallback_response(context_data)

        # Cache the result for future identical states
        self._execution_cache[state_signature] = analysis
        return analysis

    def _generate_fallback_response(self, context_data: Dict[str, Any]) -> str:
        """Generates a logic-based mock response when the API is unavailable."""
        occupancy = context_data.get('occupancy_perc', {})
        max_load = max(occupancy.values()) if occupancy else 0.0
        
        if max_load > 0.90:
            return "REASONING: Sector density exceeding 90% threshold. Immediate safety buffer required to prevent surge incident. [SIMULATION MODE] STRATEGY: Predictive Buffer."
        elif max_load > 0.85:
            return "REASONING: High congestion detected (85%+). Neighboring sectors show spare capacity. [SIMULATION MODE] STRATEGY: Direct Reroute."
        else:
            return "REASONING: Operational trends remain within healthy parameters. [SIMULATION MODE] STRATEGY: Monitor Only."

# Global singleton component
gemini_ai = GeminiReasoner()
