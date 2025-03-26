import pytest
import json
from flask import url_for


# --- /clients ---
def test_get_clients_unauthenticated(client):
    response = client.get(url_for("api.get_clients"))
    # Assuming redirect for now, adjust if API returns 401
    assert response.status_code == 302

    # Add debug logging
    print(f"Actual redirect location: {response.location}")
    print(f"Expected location: {url_for('auth.login', _external=False)}")
    print(f"Flask-Login is adding a 'next' parameter to the redirect URL")

    # Check if the location starts with the login URL (ignoring query params)
    assert response.location.startswith(url_for("auth.login", _external=False))
    # If 401: assert response.status_code == 401


def test_get_clients_authenticated(client, test_user, login):
    login(test_user)
    response = client.get(url_for("api.get_clients"))
    assert response.status_code == 200
    assert response.content_type == "application/json"
    data = json.loads(response.data)
    assert "clients" in data
    assert isinstance(data["clients"], list)  # Placeholder returns empty list


# --- /clients/<id> ---
def test_get_client_unauthenticated(client):
    response = client.get(url_for("api.get_client", client_id=1))  # Dummy ID
    assert response.status_code == 302
    # Check if the location starts with the login URL (ignoring query params)
    assert response.location.startswith(url_for("auth.login", _external=False))
    # If 401: assert response.status_code == 401


def test_get_client_authenticated(client, test_user, login, test_client_instance):
    login(test_user)
    # Use a real client ID from fixture
    response = client.get(url_for("api.get_client", client_id=test_client_instance.id))
    assert response.status_code == 200
    assert response.content_type == "application/json"
    data = json.loads(response.data)
    assert isinstance(data, dict)  # Placeholder returns empty dict


# --- /assessments ---
def test_get_assessments_unauthenticated(client):
    response = client.get(url_for("api.get_assessments"))
    assert response.status_code == 302
    # Check if the location starts with the login URL (ignoring query params)
    assert response.location.startswith(url_for("auth.login", _external=False))
    # If 401: assert response.status_code == 401


def test_get_assessments_authenticated(client, test_user, login):
    login(test_user)
    response = client.get(url_for("api.get_assessments"))
    assert response.status_code == 200
    assert response.content_type == "application/json"
    data = json.loads(response.data)
    assert "assessments" in data
    assert isinstance(data["assessments"], list)


# --- /assessments/<id> ---
def test_get_assessment_unauthenticated(client):
    response = client.get(url_for("api.get_assessment", assessment_id=1))  # Dummy ID
    assert response.status_code == 302
    # Check if the location starts with the login URL (ignoring query params)
    assert response.location.startswith(url_for("auth.login", _external=False))
    # If 401: assert response.status_code == 401


def test_get_assessment_authenticated(client, test_user, login, test_assessment):
    login(test_user)
    response = client.get(
        url_for("api.get_assessment", assessment_id=test_assessment.id)
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    data = json.loads(response.data)
    assert isinstance(data, dict)


# --- /intelligence ---
def test_get_intelligence_unauthenticated(client):
    response = client.get(url_for("api.get_intelligence"))
    assert response.status_code == 302
    # Check if the location starts with the login URL (ignoring query params)
    assert response.location.startswith(url_for("auth.login", _external=False))
    # If 401: assert response.status_code == 401


def test_get_intelligence_authenticated(client, test_user, login):
    login(test_user)
    response = client.get(url_for("api.get_intelligence"))
    assert response.status_code == 200
    assert response.content_type == "application/json"
    data = json.loads(response.data)
    assert "intelligence" in data
    assert isinstance(data["intelligence"], list)


# --- /dashboard-data ---
def test_get_dashboard_data_unauthenticated(client):
    response = client.get(url_for("api.get_dashboard_data"))
    assert response.status_code == 302
    # Check if the location starts with the login URL (ignoring query params)
    assert response.location.startswith(url_for("auth.login", _external=False))
    # If 401: assert response.status_code == 401


def test_get_dashboard_data_authenticated(client, test_user, login):
    login(test_user)
    response = client.get(url_for("api.get_dashboard_data"))
    assert response.status_code == 200
    assert response.content_type == "application/json"
    data = json.loads(response.data)
    assert "total_clients" in data
    assert "total_assessments" in data
    assert "risk_levels" in data
    assert "recent_activity" in data
