from flask import request, jsonify, render_template
from flask_login import login_required
from app.services.client_service import search_clients
from . import client_bp  # Import the blueprint from __init__.py


@client_bp.route("/api/v1/clients/search", methods=["GET"])
@login_required
def client_search():
    query = request.args.get("query")
    industry = request.args.get("industry")
    country = request.args.get("country")
    results = search_clients(query, industry, country)
    return jsonify(
        {
            "status": "success",
            "data": results,
            "meta": {"total": len(results), "page": 1, "per_page": 10},
        }
    )


@client_bp.route("/clients/search", methods=["GET"])
@login_required
def search_page():
    return render_template("client/search.html")
