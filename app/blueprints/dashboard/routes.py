"""
Routes for the dashboard blueprint
"""

import datetime
from flask import render_template
from flask_login import login_required, current_user
from . import dashboard_bp


@dashboard_bp.route("/")
@login_required
def index():
    """
    Dashboard landing page.
    Displays the Central Command Dashboard with overview metrics and summaries.
    """
    # Placeholder data - replace with actual data fetching logic later

    # Placeholder for Client Risk Overview
    clients = [
        {
            "id": 1,
            "name": "Client Alpha",
            "risk_score": 85,
            "risk_level": "High",
            "industry": "Technology",
            "last_assessment_date": datetime.date(2025, 3, 15),
        },
        {
            "id": 2,
            "name": "Client Beta",
            "risk_score": 55,
            "risk_level": "Medium",
            "industry": "Finance",
            "last_assessment_date": datetime.date(2025, 2, 20),
        },
        {
            "id": 3,
            "name": "Client Gamma",
            "risk_score": 30,
            "risk_level": "Low",
            "industry": "Healthcare",
            "last_assessment_date": datetime.date(2025, 3, 25),
        },
    ]

    # Placeholder for Key Metrics
    metrics = {
        "clients_managed": 15,
        "active_assessments": 3,
        "high_priority_findings": 8,
        "new_alerts_24h": 5,
        "assets_monitored": 120,
    }

    # Placeholder for Recent Intelligence Feed
    intelligence_items = [
        {
            "id": 101,
            "title": "New APT Campaign Targeting Finance Sector",
            "source": "Threat Intel Inc.",
            "date": datetime.date(2025, 3, 27),
        },
        {
            "id": 102,
            "title": "Geopolitical Tensions Rise in Region X",
            "source": "Global News Agency",
            "date": datetime.date(2025, 3, 26),
        },
        {
            "id": 103,
            "title": "Critical Vulnerability in Common Web Server",
            "source": "CVE Database",
            "date": datetime.date(2025, 3, 25),
        },
    ]

    return render_template(
        "dashboard/index.html",
        clients=clients,
        metrics=metrics,
        intelligence_items=intelligence_items,
    )
