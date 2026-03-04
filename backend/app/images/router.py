"""
Image upload API router.

Endpoints:
- POST /api/v1/images/upload - Upload temporary image
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import Annotated
import structlog

from app.images.service import ImageService
from app.catalog.schemas import TempImageResponse, ErrorResponse

logger = structlog.get_logger()

router = APIRouter(prefix="/images", tags=["images"])


def get_image_service() -> ImageService:
    """Dependency injection for ImageService."""
    return ImageService()


@router.post(
    "/upload",
    response_model=TempImageResponse,
    status_code=200,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file type or size"},
        500: {"model": ErrorResponse, "description": "Upload failed"},
    },
    summary="Upload temporary product image",
    description="""
    Upload a product image to temporary storage.

    Returns a temporary filename that must be included in the catalog item
    create/update request. The image will be moved to permanent storage
    when the catalog item is saved.

    **Allowed file types:** .jpg, .jpeg, .png, .gif
    **Maximum size:** 4MB
    """,
)
async def upload_image(
    file: Annotated[UploadFile, File(description="Image file to upload")],
    image_service: ImageService = Depends(get_image_service),
) -> TempImageResponse:
    """
    Upload temporary product image.

    Args:
        file: Uploaded image file
        image_service: Image service dependency

    Returns:
        Temporary filename to use in catalog item creation/update
    """
    logger.info("api.images.upload", filename=file.filename, content_type=file.content_type)

    try:
        temp_filename = await image_service.save_temp_image(file)
        return TempImageResponse(temp_filename=temp_filename)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("api.images.upload.error", filename=file.filename, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to upload image")
