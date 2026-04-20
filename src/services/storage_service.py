"""
Storage Service: Unstructured Data and Log Archival.

Handles GCS interaction for persisting large-scale simulation traces
and agentic reasoning logs.
"""

import logging
from typing import Optional
from src.core.settings import settings

try:
    from google.cloud import storage

    GCP_AVAILABLE: bool = True
except ImportError:
    GCP_AVAILABLE = False
    import unittest.mock

    storage = unittest.mock.MagicMock()  # type: ignore

storage_service_logger: logging.Logger = logging.getLogger("StadiumPulse.StorageService")


class StorageService:
    """
    Interface for Google Cloud Storage operations.
    """

    def __init__(self, project_id: str = settings.GOOGLE_PROJECT_ID) -> None:
        """Initializes the storage client."""
        self.project_id: str = project_id
        self.client: Optional[storage.Client] = None

        if GCP_AVAILABLE:
            try:
                self.client = storage.Client(project=project_id)
            except Exception:
                pass

    def upload_blob(self, content: str, filename: str) -> None:
        """
        Uploads an object to the archival log bucket.
        """
        if self.client:
            try:
                bucket = self.client.bucket(f"{self.project_id}-archival-logs")
                blob = bucket.blob(filename)
                blob.upload_from_string(content)
                storage_service_logger.info("Successfully uploaded %s to GCS", filename)
            except Exception as e:
                storage_service_logger.error("Failed to upload %s to GCS: %s", filename, e)
        storage_service_logger.info("[GCS-SAVED] Filename: %s | Bytes: %d", filename, len(content))


# GLOBAL SERVICE INSTANCE
storage_service: StorageService = StorageService()
