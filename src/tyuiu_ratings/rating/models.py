from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..profile.models import ProfileOrm

from datetime import datetime

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class RatingOrm(Base):
    __tablename__ = "ratings"

    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.applicant_id"),
        unique=False,
        nullable=False
    )
    direction: Mapped[str] = mapped_column(unique=False, nullable=False)
    rank: Mapped[int]
    date: Mapped[datetime] = mapped_column(DateTime)

    profile: Mapped["ProfileOrm"] = relationship(back_populates="ratings")
