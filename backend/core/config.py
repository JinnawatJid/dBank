from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "Deep Insights Copilot API"
    VERSION: str = "1.0.0"

    # Database Settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str

    # Read-Only Database Settings (Used by MCP SQL tool for safety)
    APP_USER: str
    APP_PASSWORD: str

    # Google AI Settings
    GOOGLE_API_KEY: Optional[str] = None

    @property
    def sync_database_url(self) -> str:
        return f"postgresql://{self.APP_USER}:{self.APP_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
