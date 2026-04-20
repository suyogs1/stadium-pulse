"""
Logging Service: Centralized Operational Auditing.

Provides unified logging interfaces for both local console diagnostics
and Google Cloud Logging for persistence and observability.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from src.core.settings import settings

try:
    from google.cloud import logging as cloud_logging

    GCP_AVAILABLE: bool = True
except ImportError:
    GCP_AVAILABLE = False
    import unittest.mock

    cloud_logging = unittest.mock.MagicMock()  # type: ignore

# Root logger for internal service tracking
service_logger: logging.Logger = logging.getLogger("StadiumPulse.LoggingService")


class LoggingService:
    """
    Manages structured log delivery to Google Cloud and terminal.

    Ensures that every agent action is recorded for post-match analysis.
    """

    def __init__(self, project_id: str = settings.GOOGLE_PROJECT_ID) -> None:
        """Initializes the logging bridge."""
        self.project_id: str = project_id
        self.client: Any = None

        if GCP_AVAILABLE and settings.ENABLE_CLOUD_LOGGING:
            try:
                self.client = cloud_logging.Client(project=project_id)
                service_logger.info("LoggingService: Cloud Logging bridge established.")
            except Exception as e:
                service_logger.warning("LoggingService: Cloud connection failed: %s", e)

    def log_event(
        self,
        agent_name: str,
        action: str,
        status: str = "SUCCESS",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Broadcasting a structured, audit-ready log event to Cloud and local clusters.
        """
        payload = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "action": action,
            "status": status,
            "metadata": metadata or {},
        }

        # Dispatch to Google Cloud Logging (Audit Cluster)
        if self.client:
            try:
                # Grouping under a dedicated 'stadium-pulse-events' log name for easier filtering
                logger_obj = self.client.logger("stadium-pulse-events")
                logger_obj.log_struct(payload, severity="INFO")
            except Exception:
                pass

        # Structured local console diagnostic
        diag_msg = f"[LOG-{status}] {agent_name}::{action} | Data: {json.dumps(metadata or {})}"
        service_logger.info(diag_msg)


# GLOBAL SERVICE INSTANCE
cloud_logger: LoggingService = LoggingService()
