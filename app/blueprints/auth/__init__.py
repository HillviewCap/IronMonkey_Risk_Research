"""
Authentication blueprint for user login, registration, and account management
"""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, template_folder='templates')

from app.blueprints.auth import routes

# Register debugging routes
from app.blueprints.auth.debug import register_debug_routes
register_debug_routes(auth_bp)
