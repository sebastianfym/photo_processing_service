from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from uuid import UUID

class ImageSchema(BaseModel):
    id: Optional[UUID] = None
    title: str = None
    filepath: str = None
    upload_time: datetime = None
    quality: str = None
    size: float = None

    class Config:
        from_attributes = True


class ImageCreateSchema(BaseModel):
    title: str = None
    quality: str = None