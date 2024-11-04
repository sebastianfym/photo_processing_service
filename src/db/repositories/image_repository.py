from datetime import datetime
from uuid import UUID

from asyncpg.pgproto.pgproto import timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import Session

from config import settings
from db.models.image import ImageModel


class ImageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    @settings.logger.catch
    async def get_image_by_id(self, image_id: UUID):
        stmt = select(ImageModel).where(ImageModel.id == image_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_images(self):
        stmt = select(ImageModel)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_media(self, media: ImageModel):
        self.session.add(media)
        await self.session.commit()
        await self.session.refresh(media)

    async def update_image(self, image_id: UUID, updated_data: dict) -> ImageModel:
        image = await self.get_image_by_id(image_id)
        if not image:
            return None
        for key, value in updated_data.items():
            setattr(image, key, value)
        await self.session.commit()
        await self.session.refresh(image)
        return image

    async def delete_image(self, image_id: UUID) -> bool:
        image = await self.get_image_by_id(image_id)
        if not image:
            return False
        await self.session.delete(image)
        await self.session.commit()
        return True
