from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "insta-1864-bot"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    verify_token: str = "change-me"
    meta_access_token: str = ""
    instagram_business_account_id: str = ""
    api_version: str = "v23.0"

    database_url: str = "sqlite:///./bot.db"
    scenario_name: str = "residence_1864"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
