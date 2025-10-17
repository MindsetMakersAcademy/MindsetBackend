from __future__ import annotations

from flasgger import Swagger
from flask import Flask

from app.api.v1.course import course_bp
from app.cli import register_cli
from app.config import Config
from app.db import db, migrate

SWAGGER_TEMPLATE = {
    "info": {
        "title": "ImpactCore API",
        "version": "1.0.0",
        "description": "Read-only APIs for **past courses** (Asia/Tehran)."
    },
    "servers": [{"url": "/"}],
}
SWAGGER_TEMPLATE["components"] = { # type: ignore
  "schemas": {
    "DeliveryMode": {
      "type": "object",
      "properties": {
        "id": {"type": "integer"},
        "label": {"type": "string"},
        "description": {"type": "string", "nullable": True}
      },
      "required": ["id", "label"]
    },
    "Venue": {
      "type": "object",
      "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "address": {"type": "string", "nullable": True},
        "map_url": {"type": "string", "nullable": True},
        "notes": {"type": "string", "nullable": True},
        "room_capacity": {"type": "integer", "nullable": True}
      },
      "required": ["id", "name"]
    },
    "Instructor": {
      "type": "object",
      "properties": {
        "id": {"type": "integer"},
        "full_name": {"type": "string"},
        "phone": {"type": "string", "nullable": True},
        "email": {"type": "string", "nullable": True},
        "bio": {"type": "string", "nullable": True}
      },
      "required": ["id", "full_name"]
    },
    "CoursePast": {
      "type": "object",
      "properties": {
        "id": {"type": "integer"},
        "title": {"type": "string"},
        "description": {"type": "string", "nullable": True},
        "capacity": {"type": "integer", "nullable": True},
        "session_counts": {"type": "integer", "nullable": True},
        "session_duration_minutes": {"type": "integer", "nullable": True},
        "start_date": {"type": "string", "format": "date", "nullable": True},
        "end_date": {"type": "string", "format": "date", "nullable": True},
        "delivery_mode": {"$ref": "#/components/schemas/DeliveryMode"},
        "venue": {"$ref": "#/components/schemas/Venue"},
        "instructors": {
          "type": "array",
          "items": {"$ref": "#/components/schemas/Instructor"}
        }
      },
      "required": ["id", "title", "delivery_mode", "instructors"]
    }
  }
}


def create_app(config: type[Config] | None = None) -> Flask:
    app = Flask(__name__)
    cfg = (config or Config)()
    app.config.from_mapping(cfg.to_flask_mapping())

    db.init_app(app)
    migrate.init_app(app, db)

    # Flasgger (Swagger UI at /docs)
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