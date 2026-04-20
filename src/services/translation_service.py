"""
Translation Service: Multilingual Operational Alerts.

Interfaces with the Google Cloud Translation API via REST for instant
multilingual communication, avoiding heavy SDK dependencies.
"""

import logging
import os
import requests
from typing import List

translation_logger = logging.getLogger("StadiumPulse.TranslationService")


class TranslationService:
    """Provides REST-based Google Cloud Translation."""

    def __init__(self) -> None:
        """Initializes the service with API key."""
        self.api_key = os.getenv("TRANSLATE_API_KEY", "")
        self.endpoint = "https://translation.googleapis.com/language/translate/v2"

    def translate_texts(self, texts: List[str], target: str = "es") -> List[str]:
        """
        Translates a list of strings to the target language via Google Cloud Translation API v2.
        """
        if not self.api_key or not texts:
            return texts

        try:
            resp = requests.post(
                self.endpoint,
                params={"key": self.api_key},
                json={"q": texts, "target": target, "format": "text"},
                timeout=4,
            )
            resp.raise_for_status()
            translations = resp.json().get("data", {}).get("translations", [])
            return [t.get("translatedText", orig) for t, orig in zip(translations, texts)]
        except Exception as exc:
            translation_logger.warning("Translation API error: %s", exc)
            return texts


translation_service = TranslationService()
