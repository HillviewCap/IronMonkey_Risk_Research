"""
Application factory pattern implementation for IronMonkey Risk Research Platform
"""

import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import redis
from elasticsearch import Elasticsearch

from config import config_dict

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()


def create_app(config_name="default"):
    """
    Factory function to create the Flask application
    Args:
        config_name: Configuration environment to use
    Returns:
        Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    print(f"Creating app with config: {config_name}")
    configuration = config_dict.get(config_name, "default")
    app.config.from_object(configuration)

    # Force development settings when running in debug
    if config_name == "development" or os.environ.get("FLASK_DEBUG") == "1":
        print("Setting explicit development configuration for cookies")
        app.config["SESSION_COOKIE_SECURE"] = False
        app.config["REMEMBER_COOKIE_SECURE"] = False
        app.config["DEBUG"] = True

    # Initialize extensions with app
    db.init_app(app)
    # Initialize login_manager BEFORE session handling (Trying this for test context issue)
    login_manager.init_app(app)
    from flask_session import Session

    Session(app)
    # Initialize other extensions
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Set up Redis connection for session storage
    try:
        app.redis = redis.from_url(app.config["REDIS_URL"])
        print(f"Redis connection established to {app.config['REDIS_URL']}")
    except Exception as e:
        print(f"Redis connection failed: {str(e)}")
        # Fall back to filesystem session if Redis fails
        app.config["SESSION_TYPE"] = "filesystem"
        print("Falling back to filesystem session storage")

    # Set up Elasticsearch connection
    try:
        es_url = app.config.get("ELASTICSEARCH_URL")
        es_user = app.config.get("ELASTICSEARCH_USER")
        es_password = app.config.get("ELASTICSEARCH_PASSWORD")

        print(f"DEBUG: Found ELASTICSEARCH_USER: {'Yes' if es_user else 'No'}")
        print(f"DEBUG: Found ELASTICSEARCH_PASSWORD: {'Yes' if es_password else 'No'}")

        if es_url:
            auth_params = {}
            if es_user and es_password:
                auth_params["basic_auth"] = (es_user, es_password)
                print("DEBUG: Adding basic_auth to Elasticsearch client")
            else:
                print("DEBUG: NOT adding basic_auth (user or password missing)")

            app.elasticsearch = Elasticsearch([es_url], **auth_params)
        else:
            app.elasticsearch = None

        if app.elasticsearch:
            print(
                f"Elasticsearch connection established to {app.config['ELASTICSEARCH_URL']}"
            )
    except Exception as e:
        print(f"Elasticsearch connection failed: {str(e)}")
        app.elasticsearch = None

    # Configure login manager with more detailed settings
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"
    login_manager.refresh_view = "auth.login"
    login_manager.needs_refresh_message = "Please reauthenticate to access this page."
    login_manager.needs_refresh_message_category = "warning"
    login_manager.session_protection = "basic"  # Use "strong" in production

    # Register blueprints
    from app.blueprints.auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.blueprints.client import client_bp

    app.register_blueprint(client_bp, url_prefix="/clients")

    from app.blueprints.risk import risk_bp

    app.register_blueprint(risk_bp, url_prefix="/risk")

    from app.blueprints.admin import admin_bp

    app.register_blueprint(admin_bp, url_prefix="/admin")

    from app.blueprints.api import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    from app.blueprints.dashboard import dashboard_bp

    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    from flask_login import current_user  # Import current_user

    @app.route("/")
    def index():
        # Handle both cases where is_authenticated could be a property or a method
        is_authenticated = current_user.is_authenticated
        if callable(is_authenticated):
            is_authenticated = is_authenticated()

        if is_authenticated:
            return redirect(url_for("dashboard.index"))
        return redirect(url_for("auth.login"))

    from datetime import datetime

    @app.context_processor
    def inject_now():
        return {"now": datetime.utcnow()}

    return app
