"""Settings configuration for the FastAPI backend."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # API settings
    api_host: str = "127.0.0.1"
    api_port: int = 0  # 0 = random available port

    # Database settings
    database_url: str = "sqlite+aiosqlite:///$DATA_DIR/auto_applier_v2.db"

    # CORS settings
    cors_origins: list[str] = ["http://localhost:5173", "tauri://localhost"]

    # Rate limiting
    rate_limit_min_minutes: int = 12
    rate_limit_max_minutes: int = 60

    # Browser settings
    browser_headless: bool = False

    # ATS handlers (which are enabled)
    enabled_ats_handlers: list[str] = ["greenhouse", "lever"]

    class Config(SettingsConfigDict):
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # Allow env vars not in model

    def __init__(self, **kwargs):
        # Replace $DATA_DIR with actual path
        super().__init__(**kwargs)

        # Set up data directory
        from . import DATA_DIR
        if DATA_DIR:
            self.database_url = self.database_url.replace("$DATA_DIR", str(DATA_DIR))


# Data directory for application data
DATA_DIR = None


def get_data_dir() -> Path:
    """Get the platform-specific data directory."""
    global DATA_DIR
    if DATA_DIR is None:
        import platform
        system = platform.system()
        home = Path.home()

        if system == "Darwin":  # macOS
            DATA_DIR = home / "Library" / "Application Support" / "AutoApplier"
        elif system == "Windows":
            DATA_DIR = home / "AppData" / "Local" / "AutoApplier"
        else:  # Linux and others
            DATA_DIR = home / ".local" / "share" / "AutoApplier"

        DATA_DIR.mkdir(parents=True, exist_ok=True)

    return DATA_DIR
