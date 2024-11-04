from typing import Optional

from pydantic import BaseModel
from uuid import UUID

class UserSchema(BaseModel):
    id: Optional[UUID]
    username: str

    class Config:
        from_attributes = True


class UserAuthSchema(BaseModel):
    username: str
    password: str


class TokenRefreshRequestSchema(BaseModel):
    refresh_token: str