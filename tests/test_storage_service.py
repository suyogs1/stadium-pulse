from unittest.mock import MagicMock, patch
from src.services.storage_service import StorageService


def test_storage_service_init_fallback():
    """Verify initialization when GCP is unavailable."""
    with patch("src.services.storage_service.GCP_AVAILABLE", False):
        service = StorageService(project_id="test")
        assert service.client is None


@patch("src.services.storage_service.storage", create=True)
@patch("src.services.storage_service.GCP_AVAILABLE", True)
def test_storage_service_init_active(mock_storage):
    """Verify initialization when GCP is available."""
    mock_client = MagicMock()
    mock_storage.Client.return_value = mock_client

    service = StorageService(project_id="test-proj")
    assert service.client is not None
    mock_storage.Client.assert_called_with(project="test-proj")


def test_upload_blob_simulation():
    """Verify upload_blob logging and simulation."""
    service = StorageService()
    service.upload_blob("test content", "test.txt")
    # Should proceed without exception


def test_upload_blob_active():
    """Verify upload_blob uses bucket and blob when client is present."""
    service = StorageService()
    service.client = MagicMock()
    service.project_id = "test-proj"
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    service.client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    service.upload_blob("content", "file.log")

    service.client.bucket.assert_called_with("test-proj-archival-logs")
    mock_bucket.blob.assert_called_with("file.log")
    mock_blob.upload_from_string.assert_called_with("content")


def test_upload_blob_exception():
    """Verify upload_blob handles exceptions gracefully."""
    service = StorageService()
    service.client = MagicMock()
    service.client.bucket.side_effect = Exception("Test exception")

    # Should not raise exception
    service.upload_blob("content", "file.log")
