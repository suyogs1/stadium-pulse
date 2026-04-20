import pytest
from unittest.mock import MagicMock, patch
from src.services.logging_service import LoggingService
from src.services.storage_service import StorageService
from src.api.server import update_stadium_state, StateUpdate


def test_logging_service_error_handling():
    """Trigger the catch-all exception block in log_event."""
    with patch("src.services.logging_service.GCP_AVAILABLE", True):
        service = LoggingService(project_id="test")
        service.client = MagicMock()
        service.client.logger.side_effect = Exception("Audit Crash")

        # This should not raise an exception, just catch and pass
        service.log_event("Agent", "Action")


def test_storage_service_missing_client():
    """Ensure upload_blob handles missing client gracefully (already tested but for safety)."""
    service = StorageService(project_id="test")
    service.client = None
    service.upload_blob("content", "name")  # Should just log and return


@pytest.mark.asyncio
async def test_api_update_fail():
    """Trigger the 500 error in /stadium/update."""
    with patch("builtins.open", side_effect=IOError("Disk Full")):
        with pytest.raises(Exception):
            await update_stadium_state(update=StateUpdate(occupancy={}, wait_times={}))
        # FastAPI handles the conversion to HTTPException if called via client,
        # but direct call will raise it.
