"""
Unit Tests for StadiumPulse Service Layer.

Validates the robust execution and fallback behavior of the
Gemini, BigQuery, and Logging services using comprehensive mocking.
"""

import unittest
from unittest.mock import MagicMock, patch
from src.services.gemini_service import VertexAIService
from src.services.bigquery_service import BigQueryService
from src.services.logging_service import LoggingService


class TestGCPServiceLayer(unittest.TestCase):
    """
    Test suite for Google Cloud Platform service abstractions.
    """

    def setUp(self) -> None:
        """Configures test context for service validation."""
        self.context_sample = {"peak_load": 0.95, "sections": ["S1", "S2"]}

    @patch("src.services.gemini_service.VERTEX_SDK_INSTALLED", False)
    def test_gemini_fallback_logic(self) -> None:
        """
        Validates that VertexAIService switches to deterministic heuristics
        when the SDK is unavailable.
        """
        from src.core.settings import settings

        with patch(
            "src.services.gemini_service.settings.GOOGLE_PROJECT_ID", settings.GOOGLE_PROJECT_ID
        ):
            service = VertexAIService()
            self.assertFalse(service.is_active)

            # High load triggers predictive buffer fallback
            result = service.execute_strategic_analysis({"peak_load": 0.95})
            self.assertIn("PREDICTIVE_BUFFER", result)

    @patch("src.services.gemini_service.VERTEX_SDK_INSTALLED", True)
    @patch("src.services.gemini_service.GenerativeModel", create=True)
    def test_gemini_active_analysis(self, mock_model) -> None:
        """
        Tests active AI reasoning flow with a mocked Vertex AI response.
        """
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value.text = "REASONING: Test. STRATEGY: Incentive."
        mock_model.return_value = mock_instance

        with patch("src.services.gemini_service.vertexai.init", create=True):
            service = VertexAIService()
            result = service.execute_strategic_analysis(self.context_sample)
            self.assertIn("Incentive", result)
            mock_instance.generate_content.assert_called_once()

    @patch("src.services.logging_service.cloud_logging.Client", create=True)
    def test_logging_service_delivery(self, mock_client_cls) -> None:
        """
        Ensures LoggingService correctly formats and delivers logs to GCP.
        """
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        from src.core.settings import settings

        with patch("src.services.logging_service.GCP_AVAILABLE", True):
            service = LoggingService(project_id=settings.GOOGLE_PROJECT_ID)
            service.log_event("TestAgent", "TestAction", status="SUCCESS", metadata={"key": "val"})

            # Verify structured log delivery
            mock_client.logger.assert_called_with("stadium-pulse-events")
            mock_client.logger().log_struct.assert_called()

    @patch("src.services.bigquery_service.bigquery.Client", create=True)
    def test_bigquery_persistence(self, mock_bq_cls) -> None:
        """
        Validates BigQueryService event recording logic.
        """
        mock_client = MagicMock()
        mock_bq_cls.return_value = mock_client

        with patch("src.services.bigquery_service.GCP_AVAILABLE", True):
            service = BigQueryService(project_id="test-proj")
            service.record_congestion_event("S1", 0.88, "REROUTE")

            # Ensure client was initialized
            self.assertIsNotNone(service.client)

    def test_historical_baseline_simulation(self) -> None:
        """Verifies BigQuery baseline retrieval logic (mocked/simulated)."""
        service = BigQueryService()
        baseline = service.get_historical_baseline(15)
        self.assertEqual(len(baseline), 12)
        self.assertTrue(all(0.0 <= v <= 1.0 for v in baseline.values()))


if __name__ == "__main__":
    unittest.main()
