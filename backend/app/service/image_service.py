import asyncio
import base64
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
import logging
import os
from time import sleep
from uuid import uuid4
from fastapi import HTTPException
from fastapi.responses import FileResponse
import numpy
import cv2


from app.database.model import Image
from app.database.repository.image import ImageRepository
from app.schema import ImgFilter, UploadRequest, DownloadRequest, UploadResponse
from app.config import UPLOAD_DIR

logger = logging.getLogger(__name__)
executor = ProcessPoolExecutor()

class ImageService:
    queue = asyncio.Queue()
    active_tasks = list()
    @staticmethod
    async def uploads_service(upload_file: UploadRequest):
        """
        Uploads an image file to the server and updates the corresponding image record in the database.

        Args:
            upload_file (UploadRequest): The request with the image to be uploaded.

        Returns:
            UploadResponse: The response containing the details of the uploaded image.

        Raises:
            HTTPException: If the image is already being processed.
        """
        if upload_file.file.content_type not in ["image/jpeg", "image/png", "image/jpg", "image/jpe", "image/tiff", "image/tif", "image/png", "image/bmp", "image/pbm", "image/pgm", "image/ppm"]:
            raise HTTPException(status_code=404, detail="Wrong file type!")
        _file_id = str(uuid4()) 
        _file_path = ImageService.create_image_file_path(upload_file.file)
        logger.info(f"Get file: {upload_file.file.filename}. Set path: {_file_path} and id: {_file_id}")
        # Cheking the same file
        _image = await ImageRepository.find_by_path(_file_path)
        if _image:
            logger.info(f"File {_file_path} already exists")
            # delete old file and save new
            ImageService.delete_image_file(_image.path)
            await ImageService.save_image_on_server(upload_file.file)
            # update record in the database
            await ImageRepository.update(_image.id, modified_at=datetime.utcnow(), filter=upload_file.filter)
            _response = UploadResponse(detail="Successfully update image!", id=_image.id, filename=_image.path.split("/")[-1], filter=upload_file.filter, modified_at=_image.modified_at)
        else:
            # save new image file
            await ImageService.save_image_on_server(upload_file.file)
            # generate record and create it in the database
            _image = Image(
                id=_file_id,
                path=_file_path,
                size=ImageService.get_image_size(_file_path),
                modified_at=datetime.utcnow(),
                mime_type=upload_file.file.content_type,
                filter=upload_file.filter,
            )
            await ImageRepository.create(**_image.dict())
            _response = UploadResponse(detail="Successfully upload image!", id=_image.id, filename=_image.path.split("/")[-1], filter=_image.filter, modified_at=_image.modified_at)
            # check that this image is not processing and add it to the queue to be processed
        if _image not in ImageService.active_tasks:
            ImageService.active_tasks.append(_image)
            await ImageService.queue.put(_image)
            return _response
        else:
            logger.info(f"File {_file_path} is processing")
            raise HTTPException(status_code=202, detail="File processing")
        

    @staticmethod
    async def downloads_service(download_file: DownloadRequest):
        """
        Handles the download of an image by its ID.

        Args:
            download_file (DownloadRequest): The request containing the image ID.

        Returns:
            FileResponse: The image file if found.

        Raises:
            HTTPException: If the image is being processed or not found.
        """
        logger.info(f"Get image id: {download_file.id}")
        # try to get the image
        _image = await ImageRepository.get_by_id(str(download_file.id))
        # check that this image is not processing
        if _image in ImageService.active_tasks:
            logger.info(f"Image with id {download_file.id} is processing")
            raise HTTPException(status_code=202, detail="Image processing")
        if _image is not None:
            logger.info(f"Image found: {_image.path}")
            return FileResponse(path=_image.path)
        logger.info(f"Image with id {download_file.id} not found")
        raise HTTPException(status_code=404, detail="Image not found!")

    @staticmethod
    async def apply_filter():
        """
        Applies a filter to an image.

        This function continuously checks the image queue for new images to process.
        It applies the specified filter to the image and logs any errors that occur.
        Once the filter has been applied, it removes the image from the active tasks list.

        Args:
            None

        Returns:
            None
        """
        while True:
            _image = await ImageService.queue.get()
            try:            
                if _image.filter == ImgFilter.INVERT:
                    await asyncio.get_event_loop().run_in_executor(executor, ImageService.use_invert_filter, _image.path)
                elif _image.filter == ImgFilter.CANNY:
                    await asyncio.get_event_loop().run_in_executor(executor, ImageService.use_canny_filter, _image.path)
            except Exception as e:
                logger.error(f"Error while filter usage: {e}")
            finally:
                logger.info(f"Filter usage completed for image: {_image.id}")
                ImageService.queue.task_done()
                ImageService.active_tasks.remove(_image)

    @staticmethod
    def create_image_file_path(file):
        """
        Create the file path for an image file.

        Args:
            file (File): The file object containing the image.

        Returns:
            str: The file path for the image.
        """
        return f"{UPLOAD_DIR}{str(file.filename)}"
    
    @staticmethod
    async def save_image_on_server(file):
        """
        Saves an image file on the server.

        Args:
            file: The image file to be saved.

        Returns:
            None
        """
        with open(f"{UPLOAD_DIR}{str(file.filename)}", "wb") as upload_file:
            upload_file_content = await file.read()
            upload_file.write(upload_file_content)
            logger.info(f"File saved: {UPLOAD_DIR}{str(file.filename)} and close")

    @staticmethod
    def get_image_size(path):
        """
        Get the size of an image file.

        Args:
            path (str): The path to the image file.

        Returns:
            int: The size of the image file in bytes.
        """
        return os.path.getsize(path)

    @staticmethod
    def delete_image_file(path):
        """
        Deletes an image file from the server.

        Args:
            path (str): The path of the image file to be deleted.

        Returns:
            None
        """
        logger.info(f"Delete file: {path}")
        try:
            os.remove(path)
        except FileNotFoundError:
            logger.info(f"File for delete not found: {path}")
            
        
    @staticmethod
    def use_invert_filter(path):        
        """
        Applies an invert filter to an image.

        Args:
            path (str): The path to the image file.

        Returns:
            None
        """
        image = cv2.imread(path)
        invert = cv2.bitwise_not(image)
        logger.info(f"Use filter: invert")
        cv2.imwrite(path, invert)
        
        
    @staticmethod
    def use_canny_filter(path):        
        """
        Applies a Canny edge detection filter to an image.

        Args:
            path (str): The path to the image file.

        Returns:
            None
        """
        t_lower = 50  # Lower Threshold 
        t_upper = 150  # Upper threshold 
        image = cv2.imread(path)
        edge = cv2.Canny(image, t_lower, t_upper)
        logger.info(f"Use filter: canny")      
        cv2.imwrite(path, edge)
