"""
Routes for the dashboard blueprint
"""

import datetime
from flask import jsonify, current_app
from flask import render_template
from datetime import datetime, timedelta, date
from flask_login import login_required, current_user
from sqlalchemy import desc, func
from sqlalchemy.orm import aliased
from . import dashboard_bp
from app import db
from app.models.client import Client
from app.models.risk import Assessment
from app.services.elasticsearch.base import ElasticsearchService


@dashboard_bp.route("/")
@login_required
def index():
    """
    Dashboard landing page.
    Displays the Central Command Dashboard with overview metrics and summaries.
    """
    # --- Client Risk Overview Data ---
    # Define risk levels and corresponding CSS classes
    risk_levels = {
        "High": {"min": 70, "max": 100, "class": "text-red-600"},
        "Medium": {"min": 40, "max": 69, "class": "text-yellow-600"},
        "Low": {"min": 0, "max": 39, "class": "text-green-600"},
    }

    # Subquery to find the latest completed assessment date for each client
    latest_assessment_subquery = db.session.query(
        Assessment.client_id,
        func.max(Assessment.assessment_date).label('latest_date')
    ).filter(
        Assessment.status == 'complete'
    ).group_by(
        Assessment.client_id
    ).subquery('latest_assessment_subquery')

    # Main query to get clients and their latest completed assessment
    top_clients_query = db.session.query(
        Client, Assessment
    ).join(
        latest_assessment_subquery,
        Client.id == latest_assessment_subquery.c.client_id
    ).join(
        Assessment,
        (Client.id == Assessment.client_id) &
        (Assessment.assessment_date == latest_assessment_subquery.c.latest_date) &
        (Assessment.status == 'complete') # Ensure we join on the completed one
    ).order_by(
        desc(Assessment.risk_score) # Order by risk score descending
    ).limit(5) # Limit to top 5

    # Process results
    clients_data = []
    for client, assessment in top_clients_query.all():
        risk_level = "N/A"
        risk_class = "text-gray-500" # Default class
        score = assessment.risk_score

        if score is not None:
            score = round(score) # Round for display
            for level, thresholds in risk_levels.items():
                if thresholds["min"] <= score <= thresholds["max"]:
                    risk_level = level
                    risk_class = thresholds["class"]
                    break

        clients_data.append({
            "id": client.id,
            "name": client.name,
            "risk_score": score,
            "risk_level": risk_level,
            "risk_class": risk_class,
            "industry": client.industry or "N/A",
            "last_assessment_date": assessment.assessment_date.strftime("%Y-%m-%d") if assessment.assessment_date else "N/A",
        })
    # --- End Client Risk Overview Data ---


    # Placeholder for Key Metrics
    metrics = {
        "clients_managed": 15,
        "active_assessments": 3,
        "high_priority_findings": 8,
        "new_alerts_24h": 5,
        "assets_monitored": 120,
    }

    # --- Recent Intelligence Feed Data ---
    intelligence_data = []
    try:
        intel_query = {
            "size": 3,
            "query": {"match_all": {}},
            "sort": [{"pub_date": {"order": "desc"}}],
            "_source": ["title", "feed_title", "pub_date"]
        }
        es_results = ElasticsearchService.search(index="threat_content", query=intel_query)

        if es_results and 'hits' in es_results and 'hits' in es_results['hits']:
            for hit in es_results['hits']['hits']:
                source = hit.get('_source', {})
                pub_date_str = source.get('pub_date')
                formatted_date = "N/A"
                if pub_date_str:
                    try:
                        # Attempt to parse ISO format (common in ES)
                        dt_obj = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                        formatted_date = dt_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        # Add other potential format parsings if needed
                        formatted_date = pub_date_str # Fallback to original string if parsing fails

                intelligence_data.append({
                    "title": source.get('title', 'No Title'),
                    "source": source.get('feed_title', 'Unknown Source'),
                    "date": formatted_date
                })
        else:
             current_app.logger.warning("Could not retrieve intelligence items from Elasticsearch or results format unexpected.")

    except Exception as e:
        current_app.logger.error(f"Error fetching intelligence items: {str(e)}")
    # --- End Recent Intelligence Feed Data ---

    # --- Top Targeted Sectors Data ---
    top_sectors_data = []
    try:
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
        sector_query = {
            "size": 0,
            "query": {
                "range": {
                    "pub_date": {
                        "gte": thirty_days_ago,
                        "format": "yyyy-MM-dd||epoch_millis" # Allow date or timestamp
                    }
                }
            },
            "aggs": {
                "top_sectors": {
                    "terms": {
                        "field": "critical_infrastructure_sectors.keyword", # Assuming this field exists and is aggregatable
                        "size": 5,
                        "order": {"_count": "desc"}
                    }
                }
            }
        }
        es_results = ElasticsearchService.search(index="threat_content", query=sector_query)

        if es_results and 'aggregations' in es_results and 'top_sectors' in es_results['aggregations'] and 'buckets' in es_results['aggregations']['top_sectors']:
            top_sectors_data = [
                {"sector": bucket['key'], "count": bucket['doc_count']}
                for bucket in es_results['aggregations']['top_sectors']['buckets']
            ]
        else:
            current_app.logger.warning("Could not retrieve top sectors aggregation from Elasticsearch or results format unexpected.")

    except Exception as e:
        current_app.logger.error(f"Error fetching top sectors: {str(e)}")
    # --- End Top Targeted Sectors Data ---



    return render_template(
        "dashboard/index.html",
        clients=clients_data, # Pass the processed data
        metrics=metrics,
        intelligence_items=intelligence_data, # Pass the fetched intelligence data
        top_sectors=top_sectors_data # Pass the top sectors data
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
