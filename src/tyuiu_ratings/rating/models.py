from datetime import datetime

from sqlalchemy import DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class RatingOrm(Base):
    __tablename__ = "ratings"

    applicant_id: Mapped[int] = mapped_column(unique=False, nullable=False)
    direction: Mapped[str] = mapped_column(unique=False, nullable=False)
    rank: Mapped[int]
    date: Mapped[datetime] = mapped_column(DateTime)

    __table_args__ = (
        UniqueConstraint("applicant_id", "direction", "date", name="unique_rating"),
    )
