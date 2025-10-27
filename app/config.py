from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass(slots=True)
class Config:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./impactcore.db")
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "0") == "1"

    def to_flask_mapping(self) -> dict[str, object]:
        return {
            "SECRET_KEY": self.SECRET_KEY,
            "SQLALCHEMY_DATABASE_URI": self.DATABASE_URL,
            "SQLALCHEMY_ECHO": self.SQL_ECHO,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }