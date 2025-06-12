from datetime import datetime

from pydantic import BaseModel


class Rating(BaseModel):
    """Позиция в рейтинге за конкретный день."""
    rank: int
    date: datetime
