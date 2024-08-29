from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Annotated
from sqlmodel import Field, SQLModel, create_engine, Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import models


router = APIRouter(prefix="/moods", tags=["moods"])


@router.get("")
async def read_moods(
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.MoodList:
    result = await session.exec(select(models.DBMood))
    moods = result.all()

    return models.MoodList.from_orm(dict(moods=moods, page_size=0, page=0, size_per_page=0))


@router.post("")
async def create_mood(
    mood: models.CreatedMood,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.MoodList:
    data = mood.dict()
    dbmood = models.DBMood(**data)
    session.add(dbmood)
    await session.commit()
    await session.refresh(dbmood)

    return models.Mood.from_orm(dbmood)