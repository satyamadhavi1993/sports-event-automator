"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # UBR
    ubr_base_url: str
    ubr_email: str
    ubr_password: str

    # Anthropic
    anthropic_api_key: str

    # Twilio SMS
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_from_number: str
    twilio_to_number: str

    # SendGrid email
    sendgrid_api_key: str
    sendgrid_from_email: str
    sendgrid_to_email: str

    # Redis
    redis_url: str = Field(default="redis://localhost:6379")

    # Sentry (optional — omit to disable)
    sentry_dsn: str | None = Field(default=None)


settings = Settings()
