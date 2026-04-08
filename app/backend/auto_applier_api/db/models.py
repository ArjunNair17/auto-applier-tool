"""SQLAlchemy models for the application database."""

from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


Base = DeclarativeBase()


class Profile(Base):
    """User profile for job applications."""
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    linkedin: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    github: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    portfolio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    work_authorization: Mapped[str] = mapped_column(String(255), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=datetime.utcnow, nullable=True)


class JobBatch(Base):
    """Batch of imported jobs (for tracking import source)."""
    __tablename__ = "job_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False)  # 'csv' or 'folder'
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id"), nullable=True)


class Job(Base):
    """Individual job to apply to."""
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    batch_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("job_batches.id"), nullable=True, index=True)
    job_url: Mapped[str] = mapped_column(Text, nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    resume_path: Mapped[str] = mapped_column(String(500), nullable=True)
    ats_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'greenhouse', 'lever', 'workday', 'ashby'
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class Application(Base):
    """Record of an application attempt."""
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # 'applied', 'failed', 'manual_required', 'skipped', 'needs_email_verification'
    application_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    intervention_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class RunSession(Base):
    """A session of applying to jobs."""
    __tablename__ = "run_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id"), nullable=False)
    stats_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string with stats


class Setting(Base):
    """Application settings."""
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, primary_key=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
