import os
from datetime import datetime, timedelta

import jwt
from passlib.context import CryptContext

from config import settings, ALGORITHM

class AuthUtilitiesService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return AuthUtilitiesService.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str):
        return AuthUtilitiesService.pwd_context.hash(password)

    @staticmethod
    def create_tokens(user_id: int, access_expires_delta: timedelta):
        to_encode = {"sub": str(user_id)}
        expire_access = datetime.utcnow() + access_expires_delta
        to_encode.update({"exp": expire_access})
        access_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        refresh_token = AuthUtilitiesService.generate_refresh_token()
        return access_token, refresh_token

    @staticmethod
    def verify_token(token: str):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

    @staticmethod
    def generate_refresh_token() -> str:
        return os.urandom(32).hex()
