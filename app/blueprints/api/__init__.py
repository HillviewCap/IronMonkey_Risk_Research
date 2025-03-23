"""
API blueprint for providing data to frontend components
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

from app.blueprints.api import routes
