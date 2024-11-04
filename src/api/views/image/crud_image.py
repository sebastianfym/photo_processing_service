from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from api.services.image_utilities import ImageUtilitiesService
from api.views.image.router import router
from config import oauth2_scheme
from db.db_service import get_session
from db.repositories.user_repository import UserRepository
from schemas.image import ImageCreateSchema
from api.services.auth_utilities import AuthUtilitiesService


@router.patch("/{image_id}", summary="Update image details")
async def update_image(image_id: UUID, updated_data: ImageCreateSchema, session: AsyncSession = Depends(get_session),
                       token: str = Depends(oauth2_scheme)):
    user_repository = UserRepository(session)
    payload = AuthUtilitiesService.verify_token(token)
    user = await user_repository.get_current_user(payload)
    if user:
        image_service = ImageUtilitiesService(session)
        return await image_service.update_image_data(image_id, updated_data)
    return HTTPException(status_code=404, detail="User not found")

@router.delete("/{image_id}", summary="Delete image")
async def delete_image(image_id: UUID, session: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)):
    user_repository = UserRepository(session)
    payload = AuthUtilitiesService.verify_token(token)
    user = await user_repository.get_current_user(payload)
    if user:
        image_service = ImageUtilitiesService(session)
        return await image_service.delete_image_data(image_id)
    return HTTPException(status_code=404, detail="User not found")