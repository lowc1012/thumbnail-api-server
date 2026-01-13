from pathlib import Path
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
        env_file=['.env.local', '.env'],
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=False
    )

    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server host address")
    PORT: int = Field(default=8080, description="Server port")
    ACCESS_LOG: bool = Field(
        default=False, description="Enable access logging"
    )
    EVENT_LOOP: str = Field(default="asyncio", description="Event loop type")

    # Application settings
    ENVIRONMENT: str = Field(
        default="development", description="Application environment"
    )
    DEBUG: bool = Field(default=True, description="Debug mode")
    ALLOW_RELOAD: bool = Field(
        default=False, description="Allow reloading"
    )
    LOG_LEVEL: str = Field(
        default="DEBUG", description="Application logging level"
    )
    DATA_DIR: Path = Field(
        default_factory=lambda: Path(__file__).parent / "data"
    )

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
