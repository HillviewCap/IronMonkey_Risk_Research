"""
Risk assessment blueprint for handling risk analysis and reporting
"""
from flask import Blueprint

risk_bp = Blueprint('risk', __name__, template_folder='templates')

from app.blueprints.risk import routes
