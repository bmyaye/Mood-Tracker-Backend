import asyncio
import pathlib
from datetime import datetime, timedelta, timezone
import sys

from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from typing import Any, Dict, Optional, AsyncIterator
from pydantic_settings import SettingsConfigDict
from sqlalchemy.future import select
from moodtracker import models, config, main, security

import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from contextlib import asynccontextmanager
from fastapi.testclient import TestClient

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

SettingsTesting = config.Settings
SettingsTesting.model_config = SettingsConfigDict(
    env_file=".testing.env", validate_assignment=True, extra="allow"
)

"""

create file .testing.env in the same level as moodtracker folder

in file .testing.env
SQLDB_URL=sqlite+aiosqlite:///./test-data/your_database_name.db

"""


@pytest.fixture(name="app", scope="session")
def app_fixture():
    settings = SettingsTesting()
    path = pathlib.Path("test-data")
    if not path.exists():
        path.mkdir()

    app = main.create_app(settings)
    asyncio.run(models.recreate_table())
    yield app

@pytest.fixture(name="client", scope="session")
def client_fixture(app: FastAPI) -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost")

@pytest_asyncio.fixture(name="session", scope="session")
async def get_session() -> AsyncIterator[models.AsyncSession]:
    settings = SettingsTesting()
    models.init_db(settings)

    async_session = models.sessionmaker(
        models.engine, class_=models.AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest_asyncio.fixture(name="user1")
async def example_user1(session: AsyncSession) -> models.DBUser:
    password = "123456"
    username = "user1"
    
    # Create user if not exists
    result = await session.exec(
        select(models.DBUser).where(models.DBUser.username == username).limit(1)
    )
    user = result.scalars().first()
    
    if user is None:
        # Add a user to the database if not present
        user = models.DBUser(
            username=username,
            email="user1@example.com",
            first_name="First",
            last_name="Last",
            password=password,
            register_date=datetime.now(timezone.utc),
            updated_date=datetime.now(timezone.utc)
        )
        session.add(user)
        await session.commit()
    
    return user

@pytest_asyncio.fixture(name="token_user1")
async def oauth_token_user1(user1: models.DBUser) -> models.Token:
    settings = SettingsTesting()
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    issued_at = user1.last_login_date or datetime.now(timezone.utc)  # Use current time if last_login_date is None
    
    return models.Token(
        access_token=security.create_access_token(
            data={"sub": user1.id},
            expires_delta=access_token_expires
        ),
        refresh_token=security.create_refresh_token(
            data={"sub": user1.id},
            expires_delta=access_token_expires,
        ),
        token_type="Bearer",
        scope="",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expires_at=datetime.now(timezone.utc) + access_token_expires,
        issued_at=issued_at,
        user_id=user1.id
    )


@pytest_asyncio.fixture(name="mood1")
async def example_mood1(session: models.AsyncSession, user1: models.DBUser) -> models.DBMood:
    description = "Feeling happy"
    mood_type = 1
    location = "Home"
    mood_date = datetime.now(tz=datetime.timezone.utc)
    
    query = await session.exec(
        models.select(models.DBMood)
        .where(models.DBMood.description == description, models.DBMood.user_id == user1.id)
        .limit(1)
    )
    mood = query.one_or_none()
    if mood:
        return mood

    mood = models.DBMood(
        description=description,
        mood_type=mood_type,
        location=location,
        mood_date=mood_date,
        user_id=user1.id
    )

    session.add(mood)
    await session.commit()
    await session.refresh(mood)
    return mood
