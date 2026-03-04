"""
Unit tests for ImageService.

Tests image upload, validation, and finalization.
Coverage target: ≥80%
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from pathlib import Path
from fastapi import UploadFile

from app.images.service import ImageService


@pytest.fixture
def image_service():
    """ImageService instance."""
    return ImageService()


@pytest.fixture
def mock_upload_file():
    """Mock UploadFile."""
    file = MagicMock(spec=UploadFile)
    file.filename = "test.png"
    file.content_type = "image/png"
    file.read = AsyncMock(side_effect=[b"chunk1", b"chunk2", b""])  # Simulate chunked read
    return file


# ============================================================================
# Save Temp Image Tests
# ============================================================================

@pytest.mark.asyncio
@patch("app.images.service.Path")
async def test_save_temp_image_success(mock_path_class, image_service, mock_upload_file):
    """Test successful temp image upload."""
    # Mock Path operations
    mock_temp_path = MagicMock()
    mock_temp_path.open = mock_open()
    mock_path_class.return_value = mock_temp_path

    # Reset read to return chunks
    mock_upload_file.read = AsyncMock(side_effect=[b"chunk" * 100, b""])

    temp_filename = await image_service.save_temp_image(mock_upload_file)

    # Assertions
    assert temp_filename.endswith(".png")
    assert len(temp_filename) == 40  # UUID (36 chars) + ".png" (4 chars)


@pytest.mark.asyncio
async def test_save_temp_image_no_filename(image_service):
    """Test upload without filename."""
    file = MagicMock(spec=UploadFile)
    file.filename = None

    with pytest.raises(Exception) as exc_info:
        await image_service.save_temp_image(file)
    assert "required" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_save_temp_image_invalid_extension(image_service):
    """Test upload with invalid file extension."""
    file = MagicMock(spec=UploadFile)
    file.filename = "test.exe"

    with pytest.raises(Exception) as exc_info:
        await image_service.save_temp_image(file)
    assert "Invalid file type" in str(exc_info.value)


@pytest.mark.asyncio
@patch("app.images.service.Path")
async def test_save_temp_image_size_exceeded(mock_path_class, image_service):
    """Test upload exceeding size limit."""
    # Mock file
    file = MagicMock(spec=UploadFile)
    file.filename = "test.png"

    # Simulate large file (> 4MB)
    large_chunk = b"x" * (5 * 1024 * 1024)  # 5MB
    file.read = AsyncMock(return_value=large_chunk)

    # Mock Path operations
    mock_temp_path = MagicMock()
    mock_temp_path.open = mock_open()
    mock_temp_path.unlink = MagicMock()
    mock_path_class.return_value = mock_temp_path

    with pytest.raises(Exception) as exc_info:
        await image_service.save_temp_image(file)
    assert "too large" in str(exc_info.value).lower()


# ============================================================================
# Finalize Image Tests
# ============================================================================

@patch("app.images.service.shutil.move")
@patch("app.images.service.Path")
def test_finalize_image_success(mock_path_class, mock_move, image_service):
    """Test successful image finalization."""
    # Mock temp path exists
    mock_temp_path = MagicMock()
    mock_temp_path.exists = MagicMock(return_value=True)

    mock_final_path = MagicMock()

    # Setup Path to return different mocks for temp and final
    def path_side_effect(arg):
        if "temp" in str(arg):
            return mock_temp_path
        return mock_final_path

    mock_path_class.side_effect = path_side_effect

    result = image_service.finalize_image("test.png")

    assert result == "test.png"
    mock_move.assert_called_once()


@patch("app.images.service.Path")
def test_finalize_image_not_found(mock_path_class, image_service):
    """Test finalization when temp file doesn't exist."""
    mock_temp_path = MagicMock()
    mock_temp_path.exists = MagicMock(return_value=False)
    mock_path_class.return_value = mock_temp_path

    with pytest.raises(Exception) as exc_info:
        image_service.finalize_image("nonexistent.png")
    assert "not found" in str(exc_info.value).lower()


# ============================================================================
# Get Final Filename Tests
# ============================================================================

def test_get_final_filename_with_temp(image_service):
    """Test getting final filename from temp filename."""
    result = image_service.get_final_filename("test.png")
    assert result == "test.png"


def test_get_final_filename_none(image_service):
    """Test getting final filename when temp is None."""
    result = image_service.get_final_filename(None)
    assert result == "dummy.png"


def test_get_final_filename_empty(image_service):
    """Test getting final filename when temp is empty string."""
    result = image_service.get_final_filename("")
    assert result == "dummy.png"


def test_get_final_filename_whitespace(image_service):
    """Test getting final filename when temp is whitespace."""
    result = image_service.get_final_filename("   ")
    assert result == "dummy.png"


# ============================================================================
# Delete Temp Image Tests
# ============================================================================

@patch("app.images.service.Path")
def test_delete_temp_image_success(mock_path_class, image_service):
    """Test deleting temp image."""
    mock_temp_path = MagicMock()
    mock_temp_path.exists = MagicMock(return_value=True)
    mock_temp_path.unlink = MagicMock()
    mock_path_class.return_value = mock_temp_path

    image_service.delete_temp_image("test.png")

    mock_temp_path.unlink.assert_called_once()


@patch("app.images.service.Path")
def test_delete_temp_image_not_found(mock_path_class, image_service):
    """Test deleting non-existent temp image (should not raise)."""
    mock_temp_path = MagicMock()
    mock_temp_path.exists = MagicMock(return_value=False)
    mock_path_class.return_value = mock_temp_path

    # Should not raise exception
    image_service.delete_temp_image("nonexistent.png")
