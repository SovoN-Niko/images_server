from fastapi import APIRouter, Depends

from app.schema import UploadRequest, DownloadRequest
from app.config import UPLOAD_DIR
from app.service.image_service import ImageService

router = APIRouter(prefix="/img_api", tags=["Image API"])


@router.post("/upload")
async def upload(request_body: UploadRequest = Depends()):
    """
    Handles the HTTP POST request to upload an image.

    Args:
        request_body (UploadRequest): The request body containing the image to be uploaded.

    Returns:
        The response from the ImageService.uploads_service method.
    """
    return await ImageService.uploads_service(request_body)


@router.get("/download")
async def download(request_body: DownloadRequest= Depends()):
    """
    Handles the HTTP GET request to download an image.

    Args:
        request_body (DownloadRequest): The request body containing the image ID.

    Returns:
        The response from the ImageService.downloads_service function.
    """
    return await ImageService.downloads_service(request_body)
