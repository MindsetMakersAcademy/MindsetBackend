from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Any

import jwt
from flask import g, jsonify, request

from app.models import Admin
from app.settings import SETTINGS


def encode_jwt(admin: Admin) -> str:
    payload = {
        "user_id": admin.id,
        "email": admin.email,
        "exp": datetime.now(UTC) + timedelta(minutes=SETTINGS.JWT_ACCESS_TOKEN_EXPIRES),
    }
    return jwt.encode(payload, SETTINGS.SECRET_KEY, algorithm=SETTINGS.JWT_ALGORITHM)


def decode_jwt(token: str) -> dict[str, object]:
    try:
        payload = jwt.decode(token, SETTINGS.SECRET_KEY, algorithms=[SETTINGS.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired") from None
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token") from None


def admin_required_jwt(fn: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(fn)
    def wrapper(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
        auth_header: str = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token: str = auth_header.split(" ", 1)[1]
        try:
            payload: dict[str, object] = decode_jwt(token)
        except ValueError as e:
            return jsonify({"error": str(e)}), 401
        g.jwt_payload = payload
        return fn(*args, **kwargs)
    return wrapper
