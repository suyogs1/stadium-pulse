"""
Tests for Recaptcha Service.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.services.recaptcha_service import RecaptchaService


class TestRecaptchaService(unittest.TestCase):
    def setUp(self):
        self.service = RecaptchaService()

    @patch("src.services.recaptcha_service.requests.post")
    def test_verify_token_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "score": 0.9}
        mock_post.return_value = mock_response

        self.service.secret_key = "fake_key"
        result = self.service.verify_token("fake_token")
        self.assertTrue(result)

    def test_verify_token_no_key(self):
        self.service.secret_key = ""
        result = self.service.verify_token("fake_token")
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
