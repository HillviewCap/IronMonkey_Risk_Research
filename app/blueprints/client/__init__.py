"""
Client management blueprint for handling client data and profiles
"""
from flask import Blueprint

client_bp = Blueprint('client', __name__, template_folder='templates')

from app.blueprints.client import routes
