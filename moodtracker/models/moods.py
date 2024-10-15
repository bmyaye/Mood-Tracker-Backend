import datetime
import pydantic
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel


class BaseMood(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    mood_type: str
    description: Optional[str] = None
    user_id: Optional[int] = 0


class CreatedMood(BaseMood):
    pass


class UpdatedMood(BaseMood):
    pass


class Mood(BaseMood):
    mood_date: Optional[datetime.datetime] = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"),
        default=None
    )


class DBMood(Mood, SQLModel, table=True):
    __tablename__ = "mood"  # Corrected __tablename__ to include double underscores
    id: Optional[int] = Field(default=None, primary_key=True)
    mood_date: datetime.datetime = Field(default_factory=datetime.datetime.now)



class MoodList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    moods: List[Mood]
    page: int
    page_size: int
    page_count: int
    size_per_page: int
