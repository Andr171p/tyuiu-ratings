from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import ForeignKey, DateTime, func, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

from src.tyuiu_ratings.constants import (
    MIN_GPA,
    MAX_GPA,
    MIN_POINTS,
    MAX_POINTS,
    MIN_EXAM_POINTS,
    MAX_EXAM_POINTS,
    MIN_BONUS_POINTS,
    MAX_BONUS_POINTS
)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(
        autoincrement=True,
        primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        onupdate=func.now()
    )


class ExamOrm(Base):
    __tablename__ = "exams"

    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.applicant_id"),
        nullable=False
    )
    name: Mapped[str]
    points: Mapped[int]

    profile: Mapped["ProfileOrm"] = relationship(back_populates="subjects")

    __table_args__ = (
        CheckConstraint(
            f"points <= {MAX_EXAM_POINTS} AND points >= {MIN_EXAM_POINTS}",
            "check_exam_points_range"
        )
    )
    

class ProfileOrm(Base):
    __tablename__ = "profiles"

    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True))
    applicant_id: Mapped[int] = mapped_column(unique=True, nullable=False, primary_key=True)
    gpa: Mapped[float]
    exams: Mapped[list["ExamOrm"]] = relationship(back_populates="profile")
    
    applicants: Mapped[list["ApplicantOrm"]] = relationship(back_populates="profile")
    history: Mapped[list["HistoryOrm"]] = relationship(back_populates="profile")

    __table_args__ = (
        Index("id_index", "user_id", "applicant_id"),
        CheckConstraint(f"gpa >= {MIN_GPA} AND gpa <= {MAX_GPA}", "check_gpa_range")
    )
    
    
class ApplicantOrm(Base):
    __tablename__ = "applicants"
    
    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.applicant_id"),
        nullable=False
    )   
    points: Mapped[int]
    bonus_points: Mapped[int]
    ratings: Mapped[int]
    institute: Mapped[str] = mapped_column(nullable=False)
    direction: Mapped[str] = mapped_column(nullable=False)
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
        )
    )
    
    
class HistoryOrm(Base):
    __tablename__ = "ratings_history"
    
    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.applicant_id"),
        nullable=False
    )   
    rating: Mapped[int]
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    applicant: Mapped["ApplicantOrm"] = relationship(back_populates="history")
    