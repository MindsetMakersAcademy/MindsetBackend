from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass(slots=True)
class Config:
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret")
    sql_alchemy_url: str = os.getenv("DATABASE_URL", "sqlite:///./impactcore.db")
    sql_echo: bool = os.getenv("SQL_ECHO", "0") == "1"

    def to_flask_mapping(self) -> dict[str, object]:
        return {
            "SECRET_KEY": self.secret_key,
            "SQLALCHEMY_DATABASE_URI": self.sql_alchemy_url,
            "SQLALCHEMY_ECHO": self.sql_echo,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }