from datetime import date
from sqlalchemy import Date
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def generate_id() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_id
    )
    event_name: Mapped[str] = mapped_column(String(200), nullable=False)
    course_name: Mapped[str] = mapped_column(
        String(200), nullable=False, default=""
    )
    issue_date: Mapped[date] = mapped_column(
        Date, nullable=False, default=date.today
    )
    status: Mapped[str] = mapped_column(
        String(30), default="pending", nullable=False
    )
    total_recipients: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    recipients: Mapped[list["Recipient"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )


class Recipient(Base):
    __tablename__ = "recipients"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_id
    )
    job_id: Mapped[str] = mapped_column(
        ForeignKey("generation_jobs.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default="pending", nullable=False
    )
    certificate_path: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    job: Mapped["GenerationJob"] = relationship(
        back_populates="recipients"
    )
