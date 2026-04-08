"""Profile business logic services."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.models import Profile
from ..db.repo import ProfileRepository
from ..db.schema import ProfileCreate, ProfileUpdate, ProfileResponse


class ProfileService:
    """Service for profile management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ProfileRepository(session)

    async def create_profile(self, data: ProfileCreate) -> ProfileResponse:
        """Create a new profile."""
        # Check if email already exists
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise ValueError(f"Profile with email {data.email} already exists")

        # Create the profile (not default if one exists)
        is_first = await self.repo.get_all() == []

        profile = await self.repo.create(
            name=data.name,
            email=data.email,
            phone=data.phone,
            linkedin=str(data.linkedin) if data.linkedin else None,
            github=str(data.github) if data.github else None,
            portfolio=str(data.portfolio) if data.portfolio else None,
            location=data.location,
            work_authorization=data.work_authorization,
            is_default=is_first,
        )

        return ProfileResponse(
            id=profile.id,
            name=profile.name,
            email=profile.email,
            phone=profile.phone,
            linkedin=data.linkedin,
            github=data.github,
            portfolio=data.portfolio,
            location=profile.location,
            work_authorization=profile.work_authorization,
            is_default=profile.is_default,
            created_at=profile.created_at,
            updated_at=None,
        )

    async def get_profile(self, profile_id: int) -> ProfileResponse:
        """Get a profile by ID."""
        profile = await self.repo.get_by_id(profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")

        return ProfileResponse(
            id=profile.id,
            name=profile.name,
            email=profile.email,
            phone=profile.phone,
            linkedin=profile.linkedin,
            github=profile.github,
            portfolio=profile.portfolio,
            location=profile.location,
            work_authorization=profile.work_authorization,
            is_default=profile.is_default,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    async def list_profiles(self) -> list[ProfileResponse]:
        """List all profiles."""
        profiles = await self.repo.get_all()
        return [
            ProfileResponse(
                id=p.id,
                name=p.name,
                email=p.email,
                phone=p.phone,
                linkedin=p.linkedin,
                github=p.github,
                portfolio=p.portfolio,
                location=p.location,
                work_authorization=p.work_authorization,
                is_default=p.is_default,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in profiles
        ]

    async def update_profile(self, profile_id: int, data: ProfileUpdate) -> ProfileResponse:
        """Update an existing profile."""
        profile = await self.repo.get_by_id(profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")

        # Only update provided fields
        update_data = {
            k: v for k, v in data.model_dump(exclude_unset=True).items()
            if v is not None
        }
        profile = await self.repo.update(profile, **update_data)

        return ProfileResponse(
            id=profile.id,
            name=profile.name,
            email=profile.email,
            phone=profile.phone,
            linkedin=profile.linkedin,
            github=profile.github,
            portfolio=profile.portfolio,
            location=profile.location,
            work_authorization=profile.work_authorization,
            is_default=profile.is_default,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    async def delete_profile(self, profile_id: int) -> None:
        """Delete a profile."""
        profile = await self.repo.get_by_id(profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")

        await self.repo.delete(profile)

    async def set_default_profile(self, profile_id: int) -> ProfileResponse:
        """Set a profile as default."""
        profile = await self.repo.set_default(profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")

        return ProfileResponse(
            id=profile.id,
            name=profile.name,
            email=profile.email,
            phone=profile.phone,
            linkedin=profile.linkedin,
            github=profile.github,
            portfolio=profile.portfolio,
            location=profile.location,
            work_authorization=profile.work_authorization,
            is_default=profile.is_default,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
