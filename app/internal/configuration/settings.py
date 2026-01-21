from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings

    Configuration precedence:
    1. Environment variables
    2. Values in `.env.local` (if exists)
    3. Values in `.env`
    4. Default values defined in class fields
    """

    model_config = SettingsConfigDict(
        env_file=[".env.local", ".env"],
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server host address")
    PORT: int = Field(default=8080, description="Server port")
    ACCESS_LOG: bool = Field(default=False, description="Enable access logging")
    EVENT_LOOP: str = Field(default="asyncio", description="Event loop type")

    # Application settings
    ENVIRONMENT: str = Field(
        default="development", description="Application environment"
    )
    DEBUG: bool = Field(default=True, description="Debug mode")
    LOG_LEVEL: str = Field(default="DEBUG", description="Application logging level")
    CELERY_BROKER_URL: str = Field(default="", description="Celery broker URL")
    CELERY_BACKEND_URL: str = Field(default="", description="Celery backend URL")
    CELERY_RESULT_DB_TABLENAMES: str = Field(
        default="", description="Celery result database table names"
    )
    S3_ENDPOINT_URL: str = Field(
        default="http://localhost:9000", description="S3 endpoint URL"
    )
    S3_REGION: str = Field(default="us-east-1", description="S3 region")
    S3_BUCKET_NAME: str = Field(default="", description="S3 bucket name")
    S3_KEY_PREFIX: str = Field(default="", description="S3 key prefix")
    AWS_ACCESS_KEY_ID: str = Field(default="", description="AWS access key ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", description="AWS secret access key")
    DATABASE_URL: str = Field(default="", description="Database URL")

    # validation
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed_levels:
            raise ValueError(f"Invalid LOG_LEVEL: {v}")
        return v.upper()

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed_envs = {"development", "staging", "production"}
        if v.lower() not in allowed_envs:
            raise ValueError(f"Invalid ENVIRONMENT: {v}")
        return v.lower()


def get_settings() -> Settings:
    """
    Get application settings.

    This function creates a new Settings instance each time it's called,
    allowing for dynamic environment variable

    Returns:
        Settings: Application configuration
    """
    return Settings()
