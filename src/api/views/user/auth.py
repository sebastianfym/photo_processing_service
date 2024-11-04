from asyncpg.pgproto.pgproto import timedelta
from starlette.status import HTTP_200_OK

from config import settings
settings.SYS_PATH

from db.repositories.user_repository import UserRepository
from api.services.auth_utilities import AuthUtilitiesService

from api.services.user_utilities import UserUtilitiesService

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from .router import router
from schemas.user import UserAuthSchema, TokenRefreshRequestSchema
from schemas.error import ErrorException

from db.db_service import get_session
from config import settings


@router.post("/login", status_code=HTTP_200_OK, summary="User authorization page", responses={
                401: {"model": ErrorException, "detail": "Unauthorized",
                      "message": "Incorrect username or password"}
            })
async def login(user_data: UserAuthSchema, session: Session = Depends(get_session)):
    user_repository = UserRepository(session)
    user = await user_repository.auth_user(user_data.username)

    if (not user) or (not AuthUtilitiesService.verify_password(user_data.password, user.password)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token, refresh_token = AuthUtilitiesService.create_tokens(
        user_id=user.id,
        access_expires_delta=timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    await user_repository.user_refresh_token(str(user.id), refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/refresh", status_code=status.HTTP_200_OK, summary="Refresh access token", responses={
                401: {"model": ErrorException, "detail": "Invalid refresh token",
                      "message": "Invalid refresh token"}
            })
async def refresh_token(request: TokenRefreshRequestSchema, session: Session = Depends(get_session)):
    user_service = UserUtilitiesService(sessions)
    refresh_token = request.refresh_token
    user_repository = UserRepository(session)

    approve_refresh_token = await user_repository.check_and_get_refresh_token(refresh_token)
    user = await user_service.get_user_by_refresh_token(user_repository, approve_refresh_token)

    access_token, refresh_token = AuthUtilitiesService.create_tokens(
        user_id=user.id,
        access_expires_delta=timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    await user_repository.user_refresh_token(str(user.id), refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token}