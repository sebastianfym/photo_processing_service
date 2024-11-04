from datetime import datetime
from uuid import UUID

from asyncpg.pgproto.pgproto import timedelta
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

# from api.services.auth_utilities import AuthUtilitiesService
from db.models.user import UserModel, RefreshTokenModel

from config import settings


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_user(self, new_user: UserModel):
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

    async def get_user_by_id(self, user_id: UUID):
        stmt = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        user = stmt.scalar_one_or_none()
        return user

    async def get_current_user(self, payload):
        try:
            user_id = payload.get("sub")
            stmt = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
            user = stmt.scalar_one_or_none()
            return user
        except AttributeError:
            return None

    async def auth_user(self, username: str):
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def user_refresh_token(self, user_id: UUID, new_refresh_token: str):
        existing_token = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id)
        )
        existing_token = existing_token.scalar_one_or_none()

        if existing_token:
            await self.session.delete(existing_token)
            await self.session.commit()
        new_token = RefreshTokenModel(
            token=new_refresh_token,
            user_id=user_id,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.session.add(new_token)
        await self.session.commit()
        await self.session.refresh(new_token)

    async def get_detail_user(self, user_id: UUID):
        stmt = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        user = stmt.scalar_one_or_none()
        return user


    async def get_user_refresh_token(self, user: UserModel):
        stmt = await self.session.execute(select(RefreshTokenModel).where(RefreshTokenModel.user == user))
        refresh_token = stmt.scalar_one_or_none()
        return refresh_token

    async def check_and_get_refresh_token(self, refresh_token: str):
        stmt = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token == refresh_token)
        )
        existing_token = stmt.scalar_one_or_none()
        return existing_token

    async def get_user_by_refresh_token(self, refresh_token: str):
        user_stmt = await self.session.execute(
            select(UserModel).where(UserModel.id == refresh_token.user_id)
        )
        user = user_stmt.scalar_one_or_none()
        return user
