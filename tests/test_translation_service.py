"""
Tests for Translation Service.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.services.translation_service import TranslationService


class TestTranslationService(unittest.TestCase):
    def setUp(self):
        self.service = TranslationService()

    @patch("src.services.translation_service.requests.post")
    def test_translate_texts_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"translations": [{"translatedText": "Hola"}]}}
        mock_post.return_value = mock_response

        self.service.api_key = "fake_key"
        result = self.service.translate_texts(["Hello"], "es")
        self.assertEqual(result, ["Hola"])

    def test_translate_texts_no_key(self):
        self.service.api_key = ""
        result = self.service.translate_texts(["Hello"], "es")
        self.assertEqual(result, ["Hello"])


if __name__ == "__main__":
    unittest.main()
