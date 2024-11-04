import os
from datetime import datetime
from typing import List, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from config import settings
from db.models.image import ImageModel
from db.repositories.image_repository import ImageRepository
from schemas.image import ImageSchema, ImageCreateSchema
from PIL import Image

from api.services.rabbit_utilities import RABBITMQ_PUBLISHER
from schemas.size import SizeEnum


class ImageUtilitiesService:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def check_image(self, image_model: ImageModel):
        if image_model is not None:
            return True
        else:
            return {"status_code":404, "detail":"Image not found"}


    async def model_conversion(self, image_model: ImageModel) -> ImageSchema:
        if image_model is not None:
            image = ImageSchema(
                id=image_model.id,
                title=image_model.title,
                filepath=image_model.filepath,
                upload_time=image_model.upload_time,
                quality=image_model.quality,
                size=image_model.size,
            )
            return image
        else:
            return None


    async def collect_all_images(self, image_list: List[ImageModel]) -> List[ImageSchema]:
        list_result = []
        for image in image_list:
            checked_image = await self.model_conversion(image)
            if checked_image:
                list_result.append(checked_image)
        return list_result


    async def convert_image_size(self, image, file, output_dir, upload_time, resolution, image_list):
        for new_size in [SizeEnum.small.value, SizeEnum.medium.value]:
            thumbnail = image.copy()
            thumbnail.thumbnail(new_size)
            thumbnail_path = os.path.join(output_dir, f"{new_size[0]}x{new_size[1]}_{file.filename}")
            thumbnail.save(thumbnail_path)
            small_size_img = ImageModel(
                title=f"{new_size[0]}x{new_size[1]}_{file.filename}",
                filepath=thumbnail_path,
                size=new_size[0],
                upload_time=upload_time,
                quality=resolution,
            )
            image_list.append(small_size_img)


    async def convert_image_to_grayscale(self, image, file, output_dir, upload_time, resolution, image_list, size):
        grayscale = image.convert("L")
        grayscale_path = os.path.join(output_dir, f"grayscale_{file.filename}")
        grayscale.save(grayscale_path)
        grayscale_img = ImageModel(
            title=f"grayscale_{file.filename}",
            filepath=grayscale_path,
            size=size,
            upload_time=upload_time,
            quality=resolution,
        )
        image_list.append(grayscale_img)


    async def handle_image_list(self, image_list):
        result_list = []
        image_repository = ImageRepository(self.session)
        for image in image_list:
            await image_repository.add_media(image)
            await RABBITMQ_PUBLISHER.notify_image_event(event_type="upload", image_model=image)
            result_list.append(ImageSchema(
                id=image.id,
                title=image.title,
                filepath=image.filepath,
                size=image.size,
                upload_time=image.upload_time,
                quality=image.quality
            ))
        return result_list

    @settings.logger.catch
    async def process_image(self, file) -> List[ImageModel]:
        image_list = []
        output_dir = settings.UPLOADED_DIR
        os.makedirs(output_dir, exist_ok=True)
        upload_time = datetime.utcnow()
        try:
            file_path = os.path.join(output_dir, file.filename)
            with open(file_path, "wb") as buffer:
                buffer.write(file.file.read())

            image = Image.open(file_path)
            size = os.path.getsize(file_path)
            resolution = f"{image.width}x{image.height}"

            await self.convert_image_size(image, file, output_dir, upload_time, resolution, image_list)
            await self.convert_image_to_grayscale(image, file, output_dir, upload_time, resolution, image_list, size)

            final_img =ImageModel(
                    title=file.filename,
                    filepath=file_path,
                    size=size,
                    upload_time=upload_time,
                    quality=resolution,
                )
            image_list.append(final_img)
            result = await self.handle_image_list(image_list)

            return result
        except Exception as e:
            raise ValueError(f"Image processing error: {e}")


    @settings.logger.catch
    async def update_image_data(self, image_id: UUID, updated_data: ImageCreateSchema):
        image_repository = ImageRepository(self.session)
        updated_image = await image_repository.update_image(image_id, updated_data.dict(exclude_unset=True))
        if not updated_image:
            raise HTTPException(status_code=404, detail="Image not found")
        await RABBITMQ_PUBLISHER.notify_image_event(event_type="updated", image_model=updated_image)
        return await self.model_conversion(updated_image)


    @settings.logger.catch
    async def delete_image_data(self, image_id: UUID) -> Dict:
        image_repository = ImageRepository(self.session)
        image_model = await image_repository.get_image_by_id(image_id)

        if not image_model:
            raise HTTPException(status_code=404, detail="Image not found")

        await RABBITMQ_PUBLISHER.notify_image_event(event_type="delete", image_model=image_model)
        file_path = image_model.filepath
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise f"File not found at {file_path}"

        await self.session.delete(image_model)
        await self.session.commit()

        return {"status_code": 200, "detail": "Image and file successfully deleted"}