from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship


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
    

class ProfileModel(Base):
    __tablename__ = "profiles"
    
    applicant_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    
    applicants: Mapped[list["ApplicantModel"]] = relationship(back_populates="profile")
    history: Mapped[list["HistoryModel"]] = relationship(back_populates="profile")
    
    
class ApplicantModel(Base):
    __tablename__ = "applicants"
    
    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("profile.applicant_id"),
        nullable=False
    )   
    points: Mapped[int]
    ratings: Mapped[int]
    institute: Mapped[str] = mapped_column(nullable=False)
    direction: Mapped[str] = mapped_column(nullable=False)
    probability: Mapped[float]
    original: Mapped[bool]
    
    profile: Mapped["ProfileModel"] = relationship(back_populates="applicants")
    
    
class HistoryModel(Base):
    __tablename__ = "ratings_history"
    
    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("profile.applicant_id"),
        nullable=False
    )   
    rating: Mapped[int]
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    applicant: Mapped["ApplicantModel"] = relationship(back_populates="history")
    