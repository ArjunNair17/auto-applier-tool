"""Database repository layer for CRUD operations."""

from typing import List, Optional, Type
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Base, Profile, Job, Application, RunSession, Setting


class BaseRepository:
    """Base repository with common CRUD operations."""

    def __init__(self, session: AsyncSession, model: Type[Base]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: int) -> Optional[Base]:
        """Get a record by ID."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Base]:
        """Get all records."""
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    async def create(self, **kwargs) -> Base:
        """Create a new record."""
        db_obj = self.model(**kwargs)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: Base, **kwargs) -> Base:
        """Update a record."""
        for key, value in kwargs.items():
            setattr(db_obj, key, value)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: Base) -> None:
        """Delete a record."""
        await self.session.delete(db_obj)
        await self.session.commit()

    async def delete_by_id(self, id: int) -> bool:
        """Delete a record by ID."""
        db_obj = await self.get_by_id(id)
        if db_obj:
            await self.delete(db_obj)
            return True
        return False


class ProfileRepository(BaseRepository):
    """Repository for Profile model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Profile)

    async def get_default(self) -> Optional[Profile]:
        """Get the default profile."""
        result = await self.session.execute(
            select(Profile).where(Profile.is_default == True)
        )
        return result.scalar_one_or_none()

    async def set_default(self, profile_id: int) -> Optional[Profile]:
        """Set a profile as default (unset all others)."""
        # Unset all profiles
        await self.session.execute(
            select(Profile).where(Profile.is_default == True)
        )
        for profile in (await self.session.execute(select(Profile))).scalars():
            profile.is_default = False

        # Set new default
        profile = await self.get_by_id(profile_id)
        if profile:
            profile.is_default = True
            await self.session.commit()

        return profile

    async def get_by_email(self, email: str) -> Optional[Profile]:
        """Get a profile by email."""
        result = await self.session.execute(
            select(Profile).where(Profile.email == email)
        )
        return result.scalar_one_or_none()


class JobRepository(BaseRepository):
    """Repository for Job model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Job)


class ApplicationRepository(BaseRepository):
    """Repository for Application model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Application)

    async def get_by_job_id(self, job_id: int) -> List[Application]:
        """Get all applications for a specific job."""
        result = await self.session.execute(
            select(Application)
            .where(Application.job_id == job_id)
            .order_by(Application.submitted_at.desc())
        )
        return list(result.scalars().all())

    async def get_stats(self) -> dict:
        """Get application statistics."""
        result = await self.session.execute(
            select(
                Application.status,
                func.count(Application.id).label('count')
            )
            .group_by(Application.status)
        )
        return {row.status: row.count for row in result}


class RunSessionRepository(BaseRepository):
    """Repository for RunSession model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, RunSession)

    async def get_active(self) -> Optional[RunSession]:
        """Get the currently active run session."""
        result = await self.session.execute(
            select(RunSession).where(RunSession.ended_at == None)
        )
        return result.scalar_one_or_none()


class SettingRepository(BaseRepository):
    """Repository for Setting model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Setting)

    async def get_all(self) -> List[Setting]:
        """Get all settings as key-value pairs."""
        result = await self.session.execute(select(Setting))
        return list(result.scalars().all())

    async def get_value(self, key: str) -> Optional[str]:
        """Get a setting value by key."""
        result = await self.session.execute(
            select(Setting.value).where(Setting.key == key)
        )
        return result.scalar_one_or_none()

    async def set_value(self, key: str, value: str) -> None:
        """Set a setting value by key (upsert)."""
        existing = await self.get_value(key)
        if existing is None:
            await self.create(key=key, value=value)
        else:
            # Find and update existing setting
            result = await self.session.execute(
                select(Setting).where(Setting.key == key)
            )
            setting = result.scalar_one()
            setting.value = value
            await self.session.commit()
