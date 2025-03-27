"""
Routes for the dashboard blueprint
"""

import datetime
from flask import jsonify, current_app
from flask import render_template
from datetime import datetime, timedelta, date
from flask_login import login_required, current_user
from . import dashboard_bp
from app.services.elasticsearch.base import ElasticsearchService


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
            "last_assessment_date": date(2025, 3, 15),
        },
        {
            "id": 2,
            "name": "Client Beta",
            "risk_score": 55,
            "risk_level": "Medium",
            "industry": "Finance",
            "last_assessment_date": date(2025, 2, 20),
        },
        {
            "id": 3,
            "name": "Client Gamma",
            "risk_score": 30,
            "risk_level": "Low",
            "industry": "Healthcare",
            "last_assessment_date": date(2025, 3, 25),
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
            "date": date(2025, 3, 27),
        },
        {
            "id": 102,
            "title": "Geopolitical Tensions Rise in Region X",
            "source": "Global News Agency",
            "date": date(2025, 3, 26),
        },
        {
            "id": 103,
            "title": "Critical Vulnerability in Common Web Server",
            "source": "CVE Database",
            "date": date(2025, 3, 25),
        },
    ]

    return render_template(
        "dashboard/index.html",
        clients=clients,
        metrics=metrics,
        intelligence_items=intelligence_items,
    )


@dashboard_bp.route("/api/global-risk-heatmap")
@login_required
def global_risk_heatmap_data():
    """
    API endpoint to provide data for the global risk heatmap.
    Aggregates event counts by country for the last 90 days.
    """
    try:
        ninety_days_ago = (datetime.utcnow() - timedelta(days=90)).strftime("%Y-%m-%d")

        es_query = {
            "size": 0,
            "query": {
                "range": {
                    "event_date": {
                        "gte": ninety_days_ago,
                        "format": "yyyy-MM-dd",  # Assuming event_date is mapped as date
                    }
                }
            },
            "aggs": {
                "events_by_country": {
                    "terms": {
                        "field": "country.keyword",  # Use .keyword field for aggregation
                        "size": 250,
                    }  # Get counts for up to 250 countries
                }
            },
        }

        es_results = ElasticsearchService.search(index="events", query=es_query)

        if es_results is None:
            # ElasticsearchService already logs the warning/error
            return jsonify({"error": "Could not connect to search service"}), 503

        # Check for aggregation results structure
        if (
            "aggregations" not in es_results
            or "events_by_country" not in es_results["aggregations"]
            or "buckets" not in es_results["aggregations"]["events_by_country"]
        ):
            current_app.logger.error(
                "Elasticsearch aggregation 'events_by_country.buckets' not found or invalid structure."
            )
            return jsonify({"error": "Failed to retrieve valid aggregation data"}), 500

        country_counts = {
            bucket["key"]: bucket["doc_count"]
            for bucket in es_results["aggregations"]["events_by_country"]["buckets"]
        }

        return jsonify(country_counts)

    except Exception as e:
        # Log the full exception for debugging
        current_app.logger.exception(f"Error generating heatmap data: {str(e)}")
        return (
            jsonify({"error": "An internal error occurred processing heatmap data"}),
            500,
        )
