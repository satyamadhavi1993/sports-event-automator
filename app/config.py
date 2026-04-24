"""Application configuration loaded from environment variables."""

import structlog
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Platform credentials
    platform_url: str
    platform_login_url: str
    platform_events_url: str
    platform_email: str
    platform_password: str

    # Event configuration
    event_organiser_name: str
    event_location_wed: str
    event_location_thu: str

    # Twilio
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_from_number: str
    twilio_to_number: str

    # SendGrid
    sendgrid_api_key: str
    sendgrid_from_email: str
    sendgrid_to_email: str


settings = Settings()


def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(20),
    )
