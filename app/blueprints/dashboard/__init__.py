"""
Dashboard blueprint for IronMonkey Risk Research Platform
"""
from flask import Blueprint

# Define the blueprint: 'dashboard', set its name, specify template folder
dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates')

# Import routes after blueprint definition to avoid circular imports
from . import routes