"""
Image upload and storage service.

Handles:
- Temporary image upload (to temp directory)
- Image validation (file type, size)
- Moving temp images to final location (/Pics/)
- Filename generation (UUID + extension)

Like-to-like behavior:
- No image cleanup on delete (legacy behavior preserved)
- Supports: .jpg, .jpeg, .png, .gif (legacy allowed types)
- Max size: 4MB (legacy limit)
"""

import uuid
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
import structlog

logger = structlog.get_logger()


# Configuration
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_FILE_SIZE = 4 * 1024 * 1024  # 4MB
TEMP_DIR = Path("backend/uploads/temp")
PICS_DIR = Path("frontend/public/Pics")


class ImageService:
    """
    Service for handling image uploads and storage.

    Workflow:
    1. Client uploads image → save_temp_image() → returns temp filename
    2. Client submits form with temp_image_name
    3. Server calls finalize_image() → moves temp to /Pics/
    4. If form validation fails, temp image stays (will be cleaned up by cron)
    """

    def __init__(self):
        """Initialize service and ensure directories exist."""
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        PICS_DIR.mkdir(parents=True, exist_ok=True)

    async def save_temp_image(self, file: UploadFile) -> str:
        """
        Save uploaded image to temporary directory.

        Args:
            file: Uploaded file from multipart/form-data

        Returns:
            Temporary filename (UUID + extension)

        Raises:
            HTTPException: If file type invalid, size too large, or upload fails
        """
        logger.info("image.upload.start", filename=file.filename)

        # Validate file extension
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            logger.warning(
                "image.upload.invalid_extension",
                filename=file.filename,
                extension=ext,
                allowed=ALLOWED_EXTENSIONS,
            )
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        # Generate unique filename
        temp_filename = f"{uuid.uuid4()}{ext}"
        temp_path = TEMP_DIR / temp_filename

        # Save file with size validation
        try:
            total_size = 0
            with temp_path.open("wb") as buffer:
                while chunk := await file.read(8192):  # Read in 8KB chunks
                    total_size += len(chunk)
                    if total_size > MAX_FILE_SIZE:
                        temp_path.unlink(missing_ok=True)  # Clean up partial file
                        logger.warning(
                            "image.upload.size_exceeded",
                            filename=file.filename,
                            size=total_size,
                            max_size=MAX_FILE_SIZE,
                        )
                        raise HTTPException(
                            status_code=400,
                            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.1f}MB",
                        )
                    buffer.write(chunk)

            logger.info(
                "image.upload.success",
                temp_filename=temp_filename,
                original_filename=file.filename,
                size=total_size,
            )
            return temp_filename

        except HTTPException:
            raise
        except Exception as e:
            logger.error("image.upload.failed", filename=file.filename, error=str(e))
            temp_path.unlink(missing_ok=True)
            raise HTTPException(status_code=500, detail="Failed to save image")

    def finalize_image(self, temp_filename: str) -> str:
        """
        Move image from temp directory to final /Pics/ directory.

        Args:
            temp_filename: Temporary filename (UUID + extension)

        Returns:
            Final filename (same as temp_filename)

        Raises:
            HTTPException: If temp file doesn't exist or move fails
        """
        temp_path = TEMP_DIR / temp_filename
        final_path = PICS_DIR / temp_filename

        if not temp_path.exists():
            logger.warning("image.finalize.not_found", temp_filename=temp_filename)
            raise HTTPException(
                status_code=404,
                detail=f"Temporary image not found: {temp_filename}",
            )

        try:
            shutil.move(str(temp_path), str(final_path))
            logger.info(
                "image.finalize.success",
                temp_filename=temp_filename,
                final_path=str(final_path),
            )
            return temp_filename

        except Exception as e:
            logger.error("image.finalize.failed", temp_filename=temp_filename, error=str(e))
            raise HTTPException(status_code=500, detail="Failed to finalize image")

    def get_final_filename(self, temp_filename: Optional[str]) -> str:
        """
        Get final filename for catalog item.

        Args:
            temp_filename: Temporary filename from upload, or None

        Returns:
            Final filename to store in database (or "dummy.png" if None)
        """
        if not temp_filename or temp_filename.strip() == "":
            return "dummy.png"
        return temp_filename

    def delete_temp_image(self, temp_filename: str) -> None:
        """
        Delete temporary image (e.g., if form validation fails).

        Args:
            temp_filename: Temporary filename to delete

        Note:
            This is a cleanup operation. Failure is logged but not raised.
        """
        temp_path = TEMP_DIR / temp_filename
        if temp_path.exists():
            try:
                temp_path.unlink()
                logger.info("image.temp.deleted", temp_filename=temp_filename)
            except Exception as e:
                logger.warning("image.temp.delete_failed", temp_filename=temp_filename, error=str(e))

    # Note: No delete_final_image() method
    # Legacy behavior: deleting catalog item does NOT delete image file
    # This is documented technical debt, preserved for like-to-like migration
