"""
reCAPTCHA Service: Automated Bot Protection.

Interfaces with Google reCAPTCHA v3 REST API to ensure actionable requests
are organic and not part of an automated DDoS pattern against the stadium endpoints.
"""

import logging
import os
import requests

recaptcha_logger = logging.getLogger("StadiumPulse.RecaptchaService")


class RecaptchaService:
    """Verifies reCAPTCHA v3 tokens via REST."""

    def __init__(self) -> None:
        self.secret_key = os.getenv("RECAPTCHA_SECRET", "")
        self.siteverify_url = "https://www.google.com/recaptcha/api/siteverify"

    def verify_token(self, token: str) -> bool:
        """
        Advisory verification of client tokens. Returns True if secret isn't configured.
        """
        if not self.secret_key or not token:
            return True

        try:
            resp = requests.post(
                self.siteverify_url,
                data={"secret": self.secret_key, "response": token},
                timeout=3,
            )
            resp.raise_for_status()
            data = resp.json()
            success = data.get("success", False)
            score = data.get("score", 0.0)
            if success and score >= 0.5:
                return True
            recaptcha_logger.warning("reCAPTCHA failed: success=%s score=%s", success, score)
            return False
        except Exception as e:
            recaptcha_logger.warning("reCAPTCHA API error: %s", e)
            return True


recaptcha_service = RecaptchaService()
