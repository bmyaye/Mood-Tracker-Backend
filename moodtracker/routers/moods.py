from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from sqlmodel import func
from sqlalchemy import func
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import models
from .. import deps

<<<<<<< Updated upstream

router = APIRouter(prefix="/moods", tags=["moods"])
=======
router = APIRouter(prefix="/moods", tags=["Moods"])
>>>>>>> Stashed changes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("")
async def read_moods(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
    page_size: int = 10
) -> models.MoodList:
    # Get total number of records
    total_count_stmt = select(func.count()).select_from(models.DBMood)
    total_count_result = await session.exec(total_count_stmt)
    total_count = total_count_result.scalar()

    offset = (page - 1) * page_size
    result_stmt = select(models.DBMood).offset(offset).limit(page_size)
    result = await session.exec(result_stmt)
    moods = result.scalars().all()

    # Ensure mood_date is included in each mood
    for mood in moods:
        assert hasattr(mood, 'mood_date')  # Ensure the field is present

    # Calculate page count
    page_count = (total_count + page_size - 1) // page_size

    return models.MoodList(
        moods=moods,
        page_size=page_size,
        page=page,
        size_per_page=len(moods),
        page_count=page_count
    )

@router.post("", response_model=models.Mood)
async def create_mood(
    mood: models.CreatedMood,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)]
) -> models.Mood:
    data = mood.model_dump(exclude={"user_id"})  # Use model_dump instead of dict
    dbmood = models.DBMood(**data, user_id=current_user.id)
    session.add(dbmood)
    await session.commit()
    await session.refresh(dbmood)
    return dbmood

@router.put("/{mood_id}")
async def update_mood(
    mood_id: int,
    mood_data: models.UpdatedMood,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    token: Annotated[str, Depends(oauth2_scheme)]
) -> models.Mood:
    # Fetch mood by ID
    mood = await session.get(models.DBMood, mood_id)
    if not mood:
        raise HTTPException(status_code=404, detail="Mood not found")

    # Update mood attributes
    for key, value in mood_data.model_dump().items():  # Use model_dump instead of dict
        setattr(mood, key, value)

    # Save changes
    await session.commit()

    # Return the updated mood with id
    return {
        "id": mood.id,
        "description": mood.description,
        "mood_type": mood.mood_type,
        "location": mood.location,
        "user_id": mood.user_id,
        "mood_date": mood.mood_date
    }
