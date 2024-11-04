from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK

from schemas.error import ErrorException
from schemas.user import UserAuthSchema
from api.services.user_utilities import UserUtilitiesService
from api.views.user.router import router
from db.db_service import get_session


@router.post("/register", status_code=201, summary="Create new user", responses={
                400: {"model": ErrorException, "detail": "User already register",
                      "message": "User already register"}
            })
async def register(user_data: UserAuthSchema, session: AsyncSession = Depends(get_session)):
    user_service = UserUtilitiesService(session)
    return await user_service.register_new_user(user_data)
