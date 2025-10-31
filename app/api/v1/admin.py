from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from werkzeug.security import check_password_hash

from app.auth.jwt import admin_required_jwt, encode_jwt
from app.dtos import AdminCreate, AdminLoginIn, AdminLoginOut, AdminUpdate
from app.exceptions import ConflictError, NotFoundError
from app.services.admin import AdminService

admin_bp = Blueprint("admin", __name__)
svc = AdminService()


# JWT-based login endpoint
@admin_bp.post("/login")
def login() -> tuple[Any, ...]:
    """
    Admin login (returns JWT)
    ---
    tags: [admins]
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email: {type: string}
              password: {type: string}
            required: [email, password]
    responses:
      200: {description: JWT token}
      401: {description: Invalid credentials}
      422: {description: Validation error}
    """
    try:
        # TODO : Make these cleaner
        payload = AdminLoginIn.model_validate_json(request.data or b"{}")
        admin = svc.get_admin_by_email(email=payload.email)
        if not admin or not check_password_hash(
            pwhash=admin.password_hash, password=payload.password
        ):
            return jsonify({"error": "Invalid credentials"}), 401
        token = encode_jwt(admin=admin)
        resp = AdminLoginOut(access_token=token)
        return jsonify(resp.model_dump()), 200

    except ValidationError as ve:
        return jsonify({"error": "validation_error", "details": ve.errors()}), 422


@admin_bp.get("/")
@admin_required_jwt
def list_admins() -> tuple[Any, ...]:
    """
    List admins
    ---
    tags: [admins]
    responses:
      200:
        description: List of admins
    """
    items = [a.model_dump() for a in svc.list_admins()]
    return jsonify(items), 200


@admin_bp.get("/<int:admin_id>")
@admin_required_jwt
def get_admin(admin_id: int) -> tuple[Any, ...]:
    """
    Get admin by id
    ---
    tags: [admins]
    parameters:
      - in: path
        name: admin_id
        schema: {type: integer}
        required: true
    responses:
      200: {description: OK}
      404: {description: Not found}
    """
    try:
        item = svc.get_admin(admin_id)
        return jsonify(item.model_dump()), 200
    except NotFoundError:
        return jsonify({"error": "Not found"}), 404


@admin_bp.post("/")
@admin_required_jwt
def create_admin() -> tuple[Any, ...]:
    """
    Create admin
    ---
    tags: [admins]
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email: {type: string}
              full_name: {type: string}
              password: {type: string}
            required: [email, full_name, password]
    responses:
      201: {description: Created}
      409: {description: Email exists}
      422: {description: Validation error}
    """
    try:
        payload = AdminCreate.model_validate_json(request.data or b"{}")
        created = svc.create_admin(payload)
        return jsonify(created.model_dump()), 201
    except ConflictError as e:
        return jsonify({"error": str(e)}), 409
    except ValidationError as ve:
        return jsonify({"error": "validation_error", "details": ve.errors()}), 422


@admin_bp.patch("/<int:admin_id>")
@admin_required_jwt
def update_admin(admin_id: int) -> tuple[Any, ...]:
    """
    Update admin
    ---
    tags: [admins]
    parameters:
      - in: path
        name: admin_id
        schema: {type: integer}
        required: true
    responses:
      200: {description: Updated}
      404: {description: Not found}
      422: {description: Validation error}
    """
    try:
        payload = AdminUpdate.model_validate_json(request.data or b"{}")
        updated = svc.update_admin(admin_id, payload)
        return jsonify(updated.model_dump()), 200
    except NotFoundError:
        return jsonify({"error": "Not found"}), 404
    except ValidationError as ve:
        return jsonify({"error": "validation_error", "details": ve.errors()}), 422


@admin_bp.delete("/<int:admin_id>")
@admin_required_jwt
def delete_admin(admin_id: int) -> tuple[Any, ...]:
    """
    Delete admin
    ---
    tags: [admins]
    parameters:
      - in: path
        name: admin_id
        schema: {type: integer}
        required: true
    responses:
      204: {description: Deleted}
      404: {description: Not found}
    """
    try:
        svc.delete_admin(admin_id)
        return "", 204
    except NotFoundError:
        return jsonify({"error": "Not found"}), 404
