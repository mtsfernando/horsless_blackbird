"""Application configuration using Pydantic BaseSettings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/horseless"
    SECRET_KEY: str = "change-me-in-production"
    CREDENTIAL_ENCRYPTION_KEY: str = "change-me-generate-with-Fernet.generate_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    OPENAI_API_KEY: str | None = None
    MAILGUN_API_KEY: str | None = None
    MAILGUN_DOMAIN: str | None = None
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
