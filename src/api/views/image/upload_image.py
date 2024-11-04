from api.services.image_utilities import ImageUtilitiesService
from api.views.image.router import router
from fastapi import Depends, UploadFile, File, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from db.db_service import get_session
from schemas.error import ErrorException

from db.repositories.user_repository import UserRepository

from config import oauth2_scheme

from api.services.auth_utilities import AuthUtilitiesService


@router.post("/upload_image", status_code=HTTP_200_OK, summary="Upload image file", responses={
                400: {"model": ErrorException, "detail": "Media content type not image",
                      "message": "Media content type not image"}}
            )
async def upload_image(file: UploadFile = File(...), session: AsyncSession = Depends(get_session),
                       token: str = Depends(oauth2_scheme)):
    user_repository = UserRepository(session)
    payload = AuthUtilitiesService.verify_token(token)
    user = await user_repository.get_current_user(payload)
    if user:
        image_service = ImageUtilitiesService(session)
        images_list = await image_service.process_image(file)
        return images_list
    else:
        return HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")