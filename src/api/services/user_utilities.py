from typing import List, Dict
from uuid import UUID

from fastapi import HTTPException
from starlette import status
from starlette.status import HTTP_400_BAD_REQUEST

from api.services.auth_utilities import AuthUtilitiesService
from db.repositories.user_repository import UserRepository
from schemas.user import UserSchema, UserAuthSchema

from db.models.user import  UserModel, RefreshTokenModel

from sqlalchemy.ext.asyncio import AsyncSession
from config import settings


class UserUtilitiesService:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_detail_user(self, user_repository: UserRepository, user_id: UUID) -> UserSchema:
        try:
            user = await user_repository.get_detail_user(user_id)
            return UserSchema.from_orm(user)
        except Exception as e:
            settings.logger.error(e)
            raise HTTPException(status_code=404, detail="User not found")


    @settings.logger.catch
    async def get_user_by_refresh_token(self, user_repository: UserRepository, refresh_token: str) -> UserModel:
        try:
            user = await user_repository.get_user_by_refresh_token(refresh_token)
            return user
        except AttributeError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


    @settings.logger.catch
    async def register_new_user(self, user_data: UserAuthSchema) -> Dict[str, str]:
        user_repository = UserRepository(self.session)

        if await user_repository.auth_user(user_data.username) is not None:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User already register")

        hashed_password = AuthUtilitiesService.get_password_hash(user_data.password)
        new_user = UserModel(username=user_data.username, password=hashed_password)
        await user_repository.register_user(new_user)
        return {"msg": "User registered successfully"}
