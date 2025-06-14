from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from ..constants import MIN_POINTS, MAX_POINTS, MIN_BONUS_POINTS, MAX_BONUS_POINTS


class ApplicantOrm(Base):
    __tablename__ = "applicants"

    applicant_id: Mapped[int] = mapped_column(unique=False, nullable=False)
    points: Mapped[int]
    bonus_points: Mapped[int]
    rank: Mapped[int]
    institute: Mapped[str] = mapped_column(nullable=False)
    direction: Mapped[str] = mapped_column(nullable=False)
    priority: Mapped[int] = mapped_column(nullable=False)
    probability: Mapped[float]
    original: Mapped[bool]

    __table_args__ = (
        UniqueConstraint("applicant_id", "direction", name="unique_applicant_direction"),
        CheckConstraint(
            f"points BETWEEN {MIN_POINTS} AND {MAX_POINTS}",
            "check_points_range"
        ),
        CheckConstraint(
            f"bonus_points BETWEEN {MIN_BONUS_POINTS} AND {MAX_BONUS_POINTS}",
            "check_bonus_points_range"
        ),
    )
