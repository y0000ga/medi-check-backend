from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(alias="DATABASE_URL")
    secret_key: str = Field(alias="SECRET_KEY")
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_access_secret_key: str = Field(
        default="change-me-access",
        alias="JWT_ACCESS_SECRET_KEY",
    )
    jwt_refresh_secret_key: str = Field(
        default="change-me-refresh",
        alias="JWT_REFRESH_SECRET_KEY",
    )
    jwt_access_token_expire_minutes: int = Field(
        default=3000,
        alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    jwt_refresh_token_expire_days: int = Field(
        default=30,
        alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS",
    )
    cors_origins: str = Field(
        default="http://localhost:8081,http://127.0.0.1:8081,https://y0000ga.github.io",
        alias="CORS_ORIGINS",
    )
    environment: str = Field(default="development", alias="ENVIRONMENT")
    sql_echo: bool = Field(default=False, alias="SQL_ECHO")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
