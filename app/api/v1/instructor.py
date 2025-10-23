from __future__ import annotations

from typing import Literal, cast

from flasgger import swag_from  # type: ignore
from flask import Blueprint, jsonify, request

from app.dtos import InstructorCreateDTO, InstructorUpdateDTO
from app.exceptions import AlreadyExistsError, NotFoundError, ValidationError
from app.services.instructor import InstructorService

from .swagger_docs import (
    CREATE_INSTRUCTOR_DOC,
    DELETE_INSTRUCTOR_DOC,
    GET_INSTRUCTOR_DOC,
    LIST_INSTRUCTORS_DOC,
    UPDATE_INSTRUCTOR_DOC,
)

instructor_bp = Blueprint("instructor", __name__)
svc = InstructorService()


@instructor_bp.get("")
@swag_from(LIST_INSTRUCTORS_DOC)
def list_instructors():
    """List all instructors."""
    q = request.args.get("q")
    sort = cast(Literal["id","full_name"],request.args.get("sort", "full_name"))
    direction = cast(Literal["asc", "desc"], request.args.get("direction", "asc")) 
    try:
        items = svc.list(q=q, sort=sort, direction=direction)
        return jsonify({"instructors": [i.model_dump() for i in items]}), 200
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@instructor_bp.get("/<int:instructor_id>")
@swag_from(GET_INSTRUCTOR_DOC)
def get_instructor(instructor_id: int):
    """Get a specific instructor by ID."""
    try:
        item = svc.get(instructor_id)
        return jsonify(item.model_dump()), 200
    except NotFoundError:
        return jsonify({"error": "Not found"}), 404


@instructor_bp.post("")
@swag_from(CREATE_INSTRUCTOR_DOC)
def create_instructor():
    """Create a new instructor."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    try:
        validated = InstructorCreateDTO.model_validate(data)
        item = svc.create(validated)
        return jsonify(item.model_dump()), 201
    except (ValidationError, AlreadyExistsError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@instructor_bp.put("/<int:instructor_id>")
@swag_from(UPDATE_INSTRUCTOR_DOC)
def update_instructor(instructor_id: int):
    """Update an existing instructor."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    try:
        validated = InstructorUpdateDTO.model_validate(data)
        item = svc.update(instructor_id, validated)
        return jsonify(item.model_dump()), 200
    except NotFoundError:
        return jsonify({"error": "Not found"}), 404
    except (ValidationError, AlreadyExistsError) as e:
        return jsonify({"error": str(e)}), 400


@instructor_bp.delete("/<int:instructor_id>")
@swag_from(DELETE_INSTRUCTOR_DOC)
def delete_instructor(instructor_id: int):
    """Delete an instructor."""
    try:
        svc.delete(instructor_id)
        return jsonify({"message": "Deleted"}), 204
    except NotFoundError:
        return jsonify({"error": "Not found"}), 404