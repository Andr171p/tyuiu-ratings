from uuid import UUID
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import ForeignKey, DateTime, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from ...constants import (
    MIN_GPA,
    MAX_GPA,
    MIN_POINTS,
    MAX_POINTS,
    MIN_EXAM_POINTS,
    MAX_EXAM_POINTS,
    MIN_BONUS_POINTS,
    MAX_BONUS_POINTS
)


class ExamOrm(Base):
    __tablename__ = "exams"

    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.applicant_id"),
        nullable=False
    )
    subject: Mapped[str]
    points: Mapped[int]

    profile: Mapped["ProfileOrm"] = relationship(back_populates="exams")

    __table_args__ = (
        CheckConstraint(
            f"points <= {MAX_EXAM_POINTS} AND points >= {MIN_EXAM_POINTS}",
            "check_exam_points_range"
        ),
    )
    

class ProfileOrm(Base):
    __tablename__ = "profiles"

    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), unique=True)
    applicant_id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    gender: Mapped[str]
    gpa: Mapped[float]

    exams: Mapped[list["ExamOrm"]] = relationship(back_populates="profile")
    applicants: Mapped[list["ApplicantOrm"]] = relationship(back_populates="profile")
    ratings: Mapped[list["RatingOrm"]] = relationship(back_populates="profile")

    __table_args__ = (
        Index("id_index", "user_id", "applicant_id"),
        CheckConstraint(f"gpa >= {MIN_GPA} AND gpa <= {MAX_GPA}", "check_gpa_range"),
        CheckConstraint("gender IN ('male', 'female')", "check_all_genders"),
    )
    
    
class ApplicantOrm(Base):
    __tablename__ = "applicants"

    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.applicant_id"),
        unique=False,
        nullable=False
    )   
    points: Mapped[int]
    bonus_points: Mapped[int]
    rating: Mapped[int]
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
    
    
class RatingOrm(Base):
    __tablename__ = "ratings"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("profiles.user_id"),
        unique=False,
        nullable=True
    )
    applicant_id: Mapped[int] = mapped_column(unique=False, nullable=False)
    direction: Mapped[str] = mapped_column(unique=False, nullable=False)
    rating: Mapped[int]
    date: Mapped[datetime] = mapped_column(DateTime)
    
    applicant: Mapped["ApplicantOrm"] = relationship(back_populates="rating_positions")
    