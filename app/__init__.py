from __future__ import annotations

from flasgger import Swagger
from flask import Flask

from app.api.v1 import admin_bp, blog_bp, course_bp
from app.api.v1.swagger_docs import SWAGGER_TEMPLATE
from app.cli import register_cli
from app.db import db, migrate
from app.settings import SETTINGS


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(SETTINGS.to_flask_mapping())

    db.init_app(app)
    migrate.init_app(app, db)

    Swagger(
        app,
        template=SWAGGER_TEMPLATE,
        config={
            "headers": [],
            "specs": [{"endpoint": "apispec_1", "route": "/apispec_1.json"}],
            "static_url_path": "/flasgger_static",
            "swagger_ui": True,
            "specs_route": "/docs",
        },
    )

    app.register_blueprint(course_bp, url_prefix="/api/v1/courses")
    app.register_blueprint(blog_bp, url_prefix="/api/v1/blogs")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admins")

    register_cli(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
