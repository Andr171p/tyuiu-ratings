from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..profile.models import ProfileOrm

from sqlalchemy import ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from ..constants import MIN_POINTS, MAX_POINTS, MIN_BONUS_POINTS, MAX_BONUS_POINTS


class ApplicantOrm(Base):
    __tablename__ = "applicant"

    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.applicant_id"),
        unique=False,
        nullable=False
    )
    points: Mapped[int]
    bonus_points: Mapped[int]
    rank: Mapped[int]
    institute: Mapped[str] = mapped_column(nullable=False)
    direction: Mapped[str] = mapped_column(nullable=False)
    priority: Mapped[int] = mapped_column(nullable=False)
    probability: Mapped[float]
    original: Mapped[bool]

    profile: Mapped["ProfileOrm"] = relationship(back_populates="applicants")

    __table_args__ = (
        Index("direction_index", "direction"),
        CheckConstraint(
            f"points >= {MIN_POINTS} AND points <= {MAX_POINTS}",
            "check_points_range"
        ),
        CheckConstraint(
            f"bonus_points >= {MIN_BONUS_POINTS} AND bonus_points <= {MAX_BONUS_POINTS}",
            "check_bonus_points_range"
        ),
    )
