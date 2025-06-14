from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Rating(BaseModel):
    """Позиция в рейтинге за конкретный день."""
    rank: int
    date: datetime

    model_config = ConfigDict(from_attributes=True)
