from uuid import UUID

from starlette.responses import FileResponse

from api.services.image_utilities import ImageUtilitiesService
from api.views.image.router import router
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

# from config import RABBITMQ_PUBLISHER
from db.db_service import get_session
from schemas.error import ErrorException

from db.repositories.image_repository import ImageRepository
from db.repositories.user_repository import UserRepository
from api.services.rabbit_utilities import RabbitMQPublisher, RABBITMQ_PUBLISHER


@router.get("/detail/{image_id}", status_code=HTTP_200_OK, summary="Get detaile image", responses={
                404: {"model": ErrorException, "detail": "Image not found",
                      "message": "Image not found"}
            })
async def get_image(image_id: str, session: AsyncSession = Depends(get_session)):
    image_repository = ImageRepository(session)
    image_service = ImageUtilitiesService(session)
    image = await image_repository.get_image_by_id(image_id)
    if image_service.check_image(image):
        return await image_service.model_conversion(image)
    else:
        raise HTTPException(status_code=image_service["status_code"], detail=image_service["detail"])


@router.get("/all", status_code=HTTP_200_OK, summary="Get all images", responses={
                400: {"model": ErrorException, "detail": "User already register",
                      "message": "User already register"}
            })
async def get_all_image(session: AsyncSession = Depends(get_session)):
    image_repository = ImageRepository(session)
    image_service = ImageUtilitiesService(session)
    images = await image_repository.get_all_images()
    images_list = await image_service.collect_all_images(images)
    if len(images_list) != 0:
        return images_list
    else:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="No images were found")


@router.get("/download/{image_id}", summary="Download the image")
async def download_image(image_id: UUID, session: AsyncSession = Depends(get_session)):
    image_repository = ImageRepository(session)
    image = await image_repository.get_image_by_id(image_id)
    if not image:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Image not found")
    await RABBITMQ_PUBLISHER.notify_image_event(event_type="download", image_model=image)
    return FileResponse(image.filepath, filename=image.title)