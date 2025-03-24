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

def create_app(config_name='default'):
    """
    Factory function to create the Flask application
    Args:
        config_name: Configuration environment to use
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    configuration = config_dict.get(config_name, 'default')
    app.config.from_object(configuration)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    # Set up Redis connection
    app.redis = redis.from_url(app.config['REDIS_URL'])
    
    # Set up Elasticsearch connection
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.blueprints.client import client_bp
    app.register_blueprint(client_bp, url_prefix='/clients')
    
    from app.blueprints.risk import risk_bp
    app.register_blueprint(risk_bp, url_prefix='/risk')
    
    from app.blueprints.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.blueprints.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    from datetime import datetime

    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    return app
