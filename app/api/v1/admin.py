from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.dtos import AdminCreate, AdminUpdate
from app.exceptions import ConflictError, NotFoundError
from app.services.admin import AdminService

admin_bp = Blueprint("admin", __name__)
svc = AdminService()


@admin_bp.get("/")
def list_admins():
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
def get_admin(admin_id: int):
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
def create_admin():
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
def update_admin(admin_id: int):
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
def delete_admin(admin_id: int):
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
