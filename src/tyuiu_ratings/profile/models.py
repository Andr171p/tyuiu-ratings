from uuid import UUID

from sqlalchemy import ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from ..constants import (
    MIN_GPA,
    MAX_GPA,
    MIN_POINTS,
    MAX_POINTS,
    MIN_EXAM_POINTS,
    MAX_EXAM_POINTS
)


class ExamOrm(Base):
    __tablename__ = "exams"

    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.applicant_id", ondelete="CASCADE"),
        nullable=False
    )
    subject: Mapped[str]
    points: Mapped[int]

    profile: Mapped["ProfileOrm"] = relationship(back_populates="exams")

    __table_args__ = (
        CheckConstraint(
            f"points BETWEEN {MAX_EXAM_POINTS} AND {MIN_EXAM_POINTS}",
            "check_exam_points_range"
        ),
    )


class ProfileOrm(Base):
    __tablename__ = "profiles"

    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), unique=True)
    applicant_id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    gender: Mapped[str]
    points: Mapped[int]
    gpa: Mapped[float]

    exams: Mapped[list["ExamOrm"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    __table_args__ = (
        Index("id_index", "user_id", "applicant_id"),
        CheckConstraint(f"points BETWEEN {MIN_POINTS} AND {MAX_POINTS}", "chack_points_range"),
        CheckConstraint(f"gpa BETWEEN {MIN_GPA} AND {MAX_GPA}", "check_gpa_range"),
        CheckConstraint("gender IN ('male', 'female')", "check_all_genders"),
    )
