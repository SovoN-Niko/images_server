from datetime import datetime
from fastapi import UploadFile, File
import logging
from typing import TypeVar, Optional

from pydantic import BaseModel, UUID4, Field
from sqlalchemy import false
from enum import Enum

T = TypeVar("T")

# get root logger
logger = logging.getLogger(__name__)


class ImgFilter(str, Enum):
    INVERT = "invert"
    CANNY = "canny"
    
class DownloadRequest(BaseModel):
    id: UUID4

class UploadRequest(BaseModel):
    file: UploadFile = File(...)    
    filter: Optional[str]
    
class UploadResponse(BaseModel):
    detail: Optional[str]
    id: Optional[UUID4]
    filename: Optional[str]
    filter: ImgFilter = Field(ImgFilter.INVERT)
    modified_at: Optional[datetime]
    
