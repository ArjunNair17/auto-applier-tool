"""Profiles API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import Profile
from ..db.schema import ProfileCreate, ProfileUpdate, ProfileResponse
from ..services.profiles import ProfileService


router = APIRouter(prefix="/profiles")


async def get_db():
    """Dependency for getting database session."""
    from ..main import app
    async for request in app.state["db"]:
        yield request


class ProfileCreate(BaseModel):
    """Model for creating a profile."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr = Field(..., max_length=255)
    phone: str = Field(..., min_length=10, max_length=20)
    linkedin: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None
    portfolio: Optional[HttpUrl] = None
    location: str = Field(..., min_length=1, max_length=255)
    work_authorization: str = Field(..., min_length=1, max_length=255)


class ProfileUpdate(BaseModel):
    """Model for updating a profile."""
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


@router.post("/", response_model=ProfileResponse)
async def create_profile(
    profile: ProfileCreate,
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """
    Create a new user profile.

    Args:
        profile: Profile data

    Returns:
        Created profile
    """
    service = ProfileService(db)
    return await service.create_profile(profile)


@router.get("/", response_model=List[ProfileResponse])
async def list_profiles(
    db: AsyncSession = Depends(get_db),
) -> List[ProfileResponse]:
    """
    List all user profiles.

    Returns:
        List of profiles
    """
    service = ProfileService(db)
    return await service.list_profiles()


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """
    Get a specific profile by ID.

    Args:
        profile_id: Profile ID

    Returns:
        Profile data
    """
    service = ProfileService(db)
    return await service.get_profile(profile_id)


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int,
    profile: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """
    Update an existing profile.

    Args:
        profile_id: Profile ID
        profile: Updated profile data

    Returns:
        Updated profile
    """
    service = ProfileService(db)
    return await service.update_profile(profile_id, profile)


@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a profile.

    Args:
        profile_id: Profile ID

    Returns:
        Success message
    """
    service = ProfileService(db)
    await service.delete_profile(profile_id)
    return {"message": "Profile deleted"}


@router.post("/{profile_id}/set-default")
async def set_default_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Set a profile as default.

    Args:
        profile_id: Profile ID

    Returns:
        Success message
    """
    service = ProfileService(db)
    await service.set_default_profile(profile_id)
    return {"message": "Profile set as default"}
