from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select, Relationship


class BaseMood(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str | None = None
    mood_type: str
    location: str
    user_id: int | None = 0


class CreatedMood(BaseMood):
    pass


class UpdatedMood(BaseMood):
    pass


class Mood(BaseMood):
    id: int


class DBMood(Mood, SQLModel, table=True):
    __tablename = "mood"
    id: Optional[int] = Field(default=None, primary_key=True)
    # user_id: int = Field(default=None, foreign_key="users.id")


class MoodList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    moods: list[Mood]
    page: int
    page_count: int
    size_per_page: int
