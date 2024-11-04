import decimal
import uuid
from email.policy import default
from enum import unique
from operator import index

from sqlalchemy import String, DateTime, Integer, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from db.database import Base

from sqlalchemy import ForeignKey
from datetime import datetime


class ImageModel(Base):
    __tablename__ = "image"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[String] = mapped_column(String(100), unique=False, index=True, nullable=False)
    filepath: Mapped[String] = mapped_column(String(250), unique=False, index=False, nullable=False)
    upload_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    quality: Mapped[String] = mapped_column(String(21), unique=False, index=True, nullable=False)
    size: Mapped[decimal.Decimal] = mapped_column(Float, nullable=False)