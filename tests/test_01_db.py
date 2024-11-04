import pytest

from schemas.user import UserAuthSchema
from src.db.models import UserModel
from sqlalchemy import select

@pytest.mark.asyncio
async def test_create_entry(async_session):
    test_data = UserAuthSchema(name="Test", password="Test")

    async with async_session() as session:
        new_entry = UserModel(**test_data.dict())
        session.add(new_entry)
        await session.commit()

        result = await session.execute(select(UserModel).filter_by(username="Test"))
        entry = result.scalar_one_or_none()
        assert entry is not None
        assert entry.name == "Test"

@pytest.mark.asyncio
async def test_read_entry(async_session):
    async with async_session() as session:
        result = await session.execute(select(UserModel).filter_by(username="Test"))
        entry = result.scalar_one_or_none()
        assert entry is not None
        assert entry.username == "Test"


@pytest.mark.asyncio
async def test_delete_entry(async_session):
    async with async_session() as session:
        result = await session.execute(select(UserModel).filter_by(username="Test"))
        entry = result.scalar_one_or_none()
        await session.delete(entry)
        await session.commit()

        result = await session.execute(select(UserModel).filter_by(username="Test"))
        deleted_entry = result.scalar_one_or_none()
        assert deleted_entry is None
