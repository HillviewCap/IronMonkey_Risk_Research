"""
Routes for the dashboard blueprint
"""
from flask import render_template
from flask_login import login_required, current_user
from . import dashboard_bp

@dashboard_bp.route('/')
@login_required
def index():
    """
    Dashboard landing page.
    Displays a summary of recent activity.
    """
    # Placeholder data - replace with actual data fetching logic later
    recent_clients = ["Client A", "Client B", "Client C"]
    open_risks = ["Risk 1", "Risk 2", "Risk 3"]
    
    return render_template('dashboard/index.html', 
                           user=current_user, 
                           recent_clients=recent_clients, 
                           open_risks=open_risks)