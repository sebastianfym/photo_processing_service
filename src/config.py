import os
import sys
from dotenv import load_dotenv
load_dotenv()

from typing import List, ClassVar

from fastapi.security import OAuth2PasswordBearer
from pydantic_settings import BaseSettings
from loguru import logger

import uvicorn



class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    UPLOADED_DIR: str

    RABBITMQ_URL: str
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str

    SERVER_DOMAIN: str
    SERVER_PORT: int

    SYS_PATH: str = ""


    ALLOWED_METHODS: List[str] = ["GET", "POST", "PATCH", "DELETE"]
    ALLOWED_HEADERS: List[str] = [
        "Content-Type",
        "Authorization",
        "Accept",
        "X-Requested-With"
    ]
    ALLOWED_ORIGINS: str = "*"


    LOG_FILE: str = "photo_processing.log"
    LOG_FORMAT: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    LOG_LEVEL: str = "DEBUG"
    LOG_ROTATION: str = "10 MB"
    LOG_COMPRESSION: str = "zip"
    LOG_SERIALIZE: bool = True

    logger: ClassVar = logger

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.SYS_PATH:
            self.SYS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        sys.path.append(self.SYS_PATH)

        logger.add(
            self.LOG_FILE,
            format=self.LOG_FORMAT,
            level=self.LOG_LEVEL,
            rotation=self.LOG_ROTATION,
            compression=self.LOG_COMPRESSION,
            serialize=self.LOG_SERIALIZE
        )


    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"



settings = Settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ALGORITHM = "HS256"
uvicorn_config = uvicorn.Config("main:app", host="0.0.0.0", port=8000, log_level="info")

