from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.auth.jwt import admin_required_jwt
from app.dtos import PostCreate, PostUpdate
from app.exceptions import ConflictError, NotFoundError
from app.services.blog import BlogService

blog_bp = Blueprint("blog", __name__)
svc = BlogService()


@blog_bp.get("/published")
def list_published():
    """
    List published posts
    ---
    tags: [blog]
    responses:
      200:
        description: List of published posts
    """
    items = [p.model_dump() for p in svc.list_published()]
    return jsonify(items), 200

@blog_bp.get("/<int:post_id>")
def get_by_id(post_id: int):
    """
    Get blog post by ID
    ---
    tags: [blog]
    parameters:
      - in: path
        name: post_id
        schema: {type: integer}
        required: true
    responses:
      200: {description: OK}
      404: {description: Not found}
    """
    try:
        item = svc.get_by_id(post_id)
        return jsonify(item.model_dump()), 200
    except NotFoundError:
        return jsonify({"error": "Not found"}), 404
      
@blog_bp.get("/slug/<string:slug>")
def get_by_slug(slug: str):
    """
    Get post by slug
    ---
    tags: [blog]
    parameters:
      - in: path
        name: slug
        schema: {type: string}
        required: true
    responses:
      200: {description: OK}
      404: {description: Not found}
    """
    try:
        item = svc.get_by_slug(slug)
        return jsonify(item.model_dump()), 200
    except NotFoundError:
        return jsonify({"error": "Not found"}), 404


@blog_bp.get("/")
def list_all():
    """
    List all posts (any status)
    ---
    tags: [blog]
    responses:
      200: {description: OK}
    """
    items = [p.model_dump() for p in svc.list_all()]
    return jsonify(items), 200


@blog_bp.get("/search")
def search_posts():
    """
    Search posts
    ---
    tags: [blog]
    parameters:
      - in: query
        name: q
        schema: {type: string}
        required: false
        description: Case-insensitive search in title/summary/content
    responses:
      200: {description: OK}
    """
    q = (request.args.get("q") or "").strip()
    items = [p.model_dump() for p in svc.search(q)] if q else []
    return jsonify(items), 200

@blog_bp.post("/")
@admin_required_jwt
def create_post():
    """
    Create post
    ---
    tags: [blog]
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
    responses:
      201: {description: Created}
      409: {description: Slug exists}
      422: {description: Validation error}
    """
    try:
        payload = PostCreate.model_validate_json(request.data or b"{}")
        created = svc.create_post(payload)
        return jsonify(created.model_dump()), 201
    except ConflictError as e:
        return jsonify({"error": str(e)}), 409
    except ValidationError as ve:
        return jsonify({"error": "validation_error", "details": ve.errors()}), 422


@blog_bp.patch("/<int:post_id>")
@admin_required_jwt
def update_post(post_id: int):
    """
    Update post
    ---
    tags: [blog]
    parameters:
      - in: path
        name: post_id
        schema: {type: integer}
        required: true
    responses:
      200: {description: Updated}
      404: {description: Not found}
      422: {description: Validation error}
    """
    try:
        payload = PostUpdate.model_validate_json(request.data or b"{}")
        updated = svc.update_post(post_id, payload)
        return jsonify(updated.model_dump()), 200
    except NotFoundError:
        return jsonify({"error": "Not found"}), 404
    except ValidationError as ve:
        return jsonify({"error": "validation_error", "details": ve.errors()}), 422


@blog_bp.delete("/<int:post_id>")
@admin_required_jwt
def delete_post(post_id: int):
    """
    Delete post
    ---
    tags: [blog]
    parameters:
      - in: path
        name: post_id
        schema: {type: integer}
        required: true
    responses:
      204: {description: Deleted}
      404: {description: Not found}
    """
    try:
        svc.delete_post(post_id)
        return "", 204
    except NotFoundError:
        return jsonify({"error": "Not found"}), 404
