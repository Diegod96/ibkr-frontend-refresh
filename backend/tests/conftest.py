"""
Test configuration and fixtures.
"""

import asyncio
import pytest
from fastapi.testclient import TestClient

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.database import Base, get_db


@pytest.fixture(scope="session")
def event_loop():
    """Create a module-level event loop for running async setup."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client(event_loop):
    """Create TestClient with an in-memory SQLite DB and override get_db dependency."""

    # Create in-memory async SQLite engine
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create DB schema
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    event_loop.run_until_complete(init_models())

    # Override get_db dependency to use our sessionmaker
    async def override_get_db():
        async with async_session() as session:
            try:
                yield session
            finally:
                await session.close()

    # Set the dependency override
    app.dependency_overrides[get_db] = override_get_db

    # Replace global database instance in app.core.database to avoid asyncpg connect attempts
    # Patch the app.core.database global database instance
    import importlib
    db_mod = importlib.import_module("app.core.database")

    class TestDatabase:
        def __init__(self, async_session):
            self.async_session = async_session

        async def connect(self):
            return None

        async def disconnect(self):
            return None

        async def get_session(self):
            async with self.async_session() as session:
                try:
                    yield session
                finally:
                    await session.close()

    db_mod.database = TestDatabase(async_session)

    with TestClient(app) as tc:
        yield tc

    # Teardown: remove override and dispose engine
    app.dependency_overrides.pop(get_db, None)
    event_loop.run_until_complete(engine.dispose())
