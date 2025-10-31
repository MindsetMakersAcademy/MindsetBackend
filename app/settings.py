from __future__ import annotations

from datetime import timedelta

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = Field(default="dev-secret", description="Flask secret key")
    DATABASE_URL: str = Field(default="sqlite:///./mindset.db", description="Database URL")
    SQL_ECHO: bool = Field(default=False, description="Enable SQL logging")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRES: int = Field(
        default=60, description=" short lifespan for access tokens in minute."
    )
    
    SUPERUSER_EMAIL: str = Field(default="admin@example.com", description="Superuser email")
    SUPERUSER_PASSWORD: str = Field(default="adminpass", description="Superuser password")
    SUPERUSER_NAME: str = Field(default="Superuser", description="Superuser name")
    
    def to_flask_mapping(self)  -> dict[str, object]:
        return {
            "SECRET_KEY": self.SECRET_KEY,
            "SQLALCHEMY_DATABASE_URI": self.DATABASE_URL,
            "SQLALCHEMY_ECHO": self.SQL_ECHO,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "JWT_ACCESS_TOKEN_EXPIRES": timedelta(minutes=self.JWT_ACCESS_TOKEN_EXPIRES),
            "JWT_ALGORITHM": self.JWT_ALGORITHM,
            "JWT_TOKEN_LOCATION" : ["headers", "cookies"]
        }

SETTINGS = Settings()