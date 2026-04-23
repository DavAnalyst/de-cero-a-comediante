import os
from flask import Flask, jsonify
from flask_cors import CORS
from .extensions import db, migrate, bcrypt
from .config import config_by_name


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # CORS — allow frontend origin (+ localhost for dev)
    allowed_origins = [app.config["FRONTEND_URL"], "http://localhost:3000", "http://127.0.0.1:3000"]
    CORS(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        supports_credentials=True,
    )

    # Blueprints
    from .routes.auth import auth_bp
    from .routes.courses import courses_bp
    from .routes.lessons import lessons_bp
    from .routes.progress import progress_bp
    from .routes.payments import payments_bp
    from .routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(courses_bp, url_prefix="/api/courses")
    app.register_blueprint(lessons_bp, url_prefix="/api/lessons")
    app.register_blueprint(progress_bp, url_prefix="/api/progress")
    app.register_blueprint(payments_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app
