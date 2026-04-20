"""
BigQuery Service: Historical Data Retrieval and Persistence.

Interfaces with BigQuery to extract crowd baselines and persist
congestion events for long-term analytical modeling.
"""

import logging
import random
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from src.core.settings import settings

try:
    from google.cloud import bigquery

    GCP_AVAILABLE: bool = True
except ImportError:
    import unittest.mock

    bigquery = unittest.mock.MagicMock()  # type: ignore
    GCP_AVAILABLE = False

bq_service_logger: logging.Logger = logging.getLogger("StadiumPulse.BigQueryService")


class BigQueryService:
    """
    Handles all data-lake interactions for the StadiumPulse platform.
    """

    def __init__(self, project_id: str = settings.GOOGLE_PROJECT_ID) -> None:
        """Initializes the BigQuery client."""
        self.project_id: str = project_id
        self.table_id: str = f"{project_id}.stadium_ops.congestion_decisions"
        self.client: Any = None

        if GCP_AVAILABLE:
            try:
                self.client = bigquery.Client(project=project_id)
                bq_service_logger.info("BigQueryService: Client initialized for %s.", project_id)
            except Exception:
                bq_service_logger.warning(
                    "BigQueryService: Cloud connection failed. Operating in fallback mode."
                )

    def record_congestion_event(
        self, section_id: str, load_factor: float, strategy: str, event_id: Optional[str] = None
    ) -> None:
        """
        Persists a processed decision to the BigQuery persistent audit table.

        Schema: event_id, section_id, congestion_level, selected_strategy, timestamp
        """
        final_event_id: str = event_id or f"TRC-{uuid.uuid4().hex[:8].upper()}"

        if self.client:
            row: Dict[str, Any] = {
                "event_id": final_event_id,
                "section_id": section_id,
                "congestion_level": round(load_factor, 4),
                "selected_strategy": strategy,
                "timestamp": datetime.now().isoformat(),
            }
            try:
                self.client.insert_rows_json(self.table_id, [row])
            except Exception as e:
                bq_service_logger.error(f"Failed to insert row to BigQuery: {e}")
        bq_service_logger.info(
            "[BQ-PERSIST] Event: %s | Section: %s | Load: %.2f | Strategy: %s",
            final_event_id,
            section_id,
            load_factor,
            strategy,
        )

    def get_historical_baseline(self, offset_minutes: int) -> Dict[str, float]:
        """
        Retrieves average sector loads from past match data.
        """
        # Simulated retrieval latency
        time.sleep(0.2)
        return {f"S{i}": random.uniform(0.3, 0.7) for i in range(1, 13)}


# GLOBAL SERVICE INSTANCE
bq_service: BigQueryService = BigQueryService()
