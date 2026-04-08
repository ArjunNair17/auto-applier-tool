"""Settings API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List


router = APIRouter(prefix="/settings")


class SettingsUpdate(BaseModel):
    """Model for updating settings."""
    browser_headless: Optional[bool] = None
    rate_limit_min_minutes: Optional[int] = None
    rate_limit_max_minutes: Optional[int] = None
    enabled_ats_handlers: Optional[List[str]] = None
    data_directory: Optional[str] = None


class SettingsResponse(BaseModel):
    """Model for settings response."""
    browser_headless: bool
    rate_limit_min_minutes: int
    rate_limit_max_minutes: int
    enabled_ats_handlers: List[str]
    data_directory: str


@router.get("/", response_model=SettingsResponse)
async def get_settings() -> SettingsResponse:
    """
    Get current application settings.

    Returns:
        Current settings
    """
    # TODO: Implement actual settings retrieval
    from ..settings import settings
    return SettingsResponse(
        browser_headless=settings.browser_headless,
        rate_limit_min_minutes=settings.rate_limit_min_minutes,
        rate_limit_max_minutes=settings.rate_limit_max_minutes,
        enabled_ats_handlers=settings.enabled_ats_handlers,
        data_directory=str(settings.get_data_dir()),
    )


@router.put("/", response_model=SettingsResponse)
async def update_settings(settings_update: SettingsUpdate) -> SettingsResponse:
    """
    Update application settings.

    Args:
        settings_update: Settings to update

    Returns:
        Updated settings
    """
    # TODO: Implement actual settings update
    from ..settings import settings
    return SettingsResponse(
        browser_headless=settings.browser_headless,
        rate_limit_min_minutes=settings.rate_limit_min_minutes,
        rate_limit_max_minutes=settings.rate_limit_max_minutes,
        enabled_ats_handlers=settings.enabled_ats_handlers,
        data_directory=str(settings.get_data_dir()),
    )
