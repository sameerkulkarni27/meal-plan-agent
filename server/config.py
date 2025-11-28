from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Email configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    sender_email: str = ""

    # App configuration
    app_name: str = "Meal Plan Scheduler"
    debug: bool = False

    class Config:
        # Look for .env in the same directory
        env_file = str(Path(__file__).parent / ".env")
        env_file_encoding = "utf-8"


settings = Settings()
