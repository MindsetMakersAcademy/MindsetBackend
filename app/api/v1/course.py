from __future__ import annotations

from flasgger import swag_from  # type: ignore
from flask import Blueprint, jsonify, request

from app.api.v1.swagger_docs import (
    CREATE_COURSE_DOC,
    GET_COURSE_DOC,
    LIST_COURSES_DOC,
    LIST_PAST_COURSES_DOC,
    SEARCH_COURSES_DOC,
)
from app.dtos import (
    CourseCreateIn,
    CourseListOut,
    CourseOut,
    CoursePastOut,
    CourseUpdateIn,
)
from app.exceptions import NotFoundError
from app.services.course import CourseService
from app.auth.jwt import admin_required_jwt

course_bp = Blueprint("course", __name__)
svc = CourseService()


@course_bp.get("")
@swag_from(LIST_COURSES_DOC)
def list_courses():
    """List all courses."""
    items = svc.list_courses()
    return jsonify({"courses": [CourseListOut.model_validate(i).model_dump() for i in items]}), 200


@course_bp.get("/<int:course_id>")
@swag_from(GET_COURSE_DOC)
def get_course(course_id: int):
    """Get a specific course by ID."""
    try:
        item = svc.get_course_by_id(course_id)
        return jsonify(CourseOut.model_validate(item).model_dump()), 200
    except NotFoundError:
        return jsonify({"error": "Not found"}), 404


@course_bp.get("/past")
@swag_from(LIST_PAST_COURSES_DOC)
def list_past():
    """List all past courses."""
    items = svc.list_past_courses()
    return jsonify({"courses": [CoursePastOut.model_validate(i).model_dump() for i in items]}), 200


@course_bp.get("/search")
@swag_from(SEARCH_COURSES_DOC)
def search_courses():
    """Search for courses."""
    q = (request.args.get("q") or "").strip()
    items = svc.search_courses(q) if q else []
    return jsonify({"courses": [CourseListOut.model_validate(i).model_dump() for i in items]}), 200


@course_bp.post("")
@swag_from(CREATE_COURSE_DOC)
@admin_required_jwt
def create_course():
    """Create a new course."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    try:
        validated = CourseCreateIn.model_validate(data)
        item = svc.create_course(validated)
        return jsonify(CourseOut.model_validate(item).model_dump()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


# TODO: Add swagger doc for this
@course_bp.delete("/<int:course_id>")
@admin_required_jwt
def delete_course(course_id: int):
    """Delete an existing course."""
    try:
        item = svc.delete_course(course_id)
        course_record = CourseOut.model_validate(item).model_dump()
        msg = {
            "info": f"successflly deleted course {course_id}.",
            "course_record": course_record,
        }
        return jsonify(msg), 200
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# TODO: Add swagger doc for this
@course_bp.put("/<int:course_id>")
@admin_required_jwt
def update_course(course_id: int):
    """Update an existing course."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    try:
        validated = CourseUpdateIn.model_validate(data)
        item = svc.update_course(course_id, validated)
        return jsonify(CourseOut.model_validate(item).model_dump()), 200
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
