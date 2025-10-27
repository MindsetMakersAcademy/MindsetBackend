from __future__ import annotations

from flasgger import Swagger
from flask import Flask

from app.api.v1.course import course_bp
from app.api.v1.swagger_docs import SWAGGER_TEMPLATE
from app.cli import register_cli
from app.config import Config
from app.db import db, migrate


def create_app(config: type[Config] | None = None) -> Flask:
    app = Flask(__name__)
    cfg = (config or Config)()
    app.config.from_mapping(cfg.to_flask_mapping())

    db.init_app(app)
    migrate.init_app(app, db)

    Swagger(app, template=SWAGGER_TEMPLATE, config={
        "headers": [],
        "specs": [{"endpoint": "apispec_1", "route": "/apispec_1.json"}],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs",
    })

    app.register_blueprint(course_bp, url_prefix="/api/v1/courses")

    register_cli(app)
    
    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app