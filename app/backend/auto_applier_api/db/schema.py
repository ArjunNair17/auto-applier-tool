"""Pydantic schemas for API input/output validation."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional


# Profile schemas
class ProfileCreate(BaseModel):
    """Schema for creating a profile."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr = Field(..., max_length=255)
    phone: str = Field(..., min_length=10, max_length=20)
    linkedin: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None
    portfolio: Optional[HttpUrl] = None
    location: str = Field(..., min_length=1, max_length=255)
    work_authorization: str = Field(..., min_length=1, max_length=255)


class ProfileUpdate(BaseModel):
    """Schema for updating a profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    linkedin: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None
    portfolio: Optional[HttpUrl] = None
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    work_authorization: Optional[str] = Field(None, min_length=1, max_length=255)


class ProfileResponse(BaseModel):
    """Schema for profile response."""
    id: int
    name: str
    email: str
    phone: str
    linkedin: Optional[HttpUrl]
    github: Optional[HttpUrl]
    portfolio: Optional[HttpUrl]
    location: str
    work_authorization: str
    is_default: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# Job schemas
class JobCreate(BaseModel):
    """Schema for creating/importing a job."""
    job_url: str = Field(..., min_length=1)
    company: str = Field(..., min_length=1, max_length=255)


class JobResponse(BaseModel):
    """Schema for job response."""
    id: int
    job_url: str
    company: str
    resume_path: Optional[str] = None
    ats_type: Optional[str] = None
    status: str


# Application schemas
class ApplicationResponse(BaseModel):
    """Schema for application response."""
    id: int
    job_id: int
    status: str
    application_url: Optional[str] = None
    notes: Optional[str] = None
    intervention_reason: Optional[str] = None
    submitted_at: Optional[datetime] = None


# Run schemas
class StartRunRequest(BaseModel):
    """Schema for starting a run."""
    profile_id: int = Field(..., gt=0)


class RunResponse(BaseModel):
    """Schema for run response."""
    id: int
    status: str  # idle, running, paused, stopped
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    profile_id: int


# Settings schemas
class SettingsUpdate(BaseModel):
    """Schema for updating settings."""
    browser_headless: Optional[bool] = None
    rate_limit_min_minutes: Optional[int] = Field(None, ge=1, le=120)
    rate_limit_max_minutes: Optional[int] = Field(None, ge=1, le=120)
    enabled_ats_handlers: Optional[list[str]] = None
    data_directory: Optional[str] = None


class SettingsResponse(BaseModel):
    """Schema for settings response."""
    browser_headless: bool
    rate_limit_min_minutes: int
    rate_limit_max_minutes: int
    enabled_ats_handlers: list[str]
    data_directory: str
