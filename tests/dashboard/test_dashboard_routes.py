import pytest
from flask import url_for


def test_dashboard_unauthenticated(client):
    """
    GIVEN unauthenticated user
    WHEN the '/dashboard/' page is requested (GET)
    THEN check it redirects to login with the next parameter
    """
    response = client.get(url_for("dashboard.index"))
    from urllib.parse import urlparse, parse_qs

    assert response.status_code == 302

    # Parse the actual redirect location
    actual_location_parsed = urlparse(response.location)
    actual_query_params = parse_qs(actual_location_parsed.query)

    # Check the base path is the login URL
    assert actual_location_parsed.path == url_for("auth.login")

    # Check the 'next' parameter matches the expected dashboard URL
    assert "next" in actual_query_params
    assert actual_query_params["next"][0] == url_for("dashboard.index")


def test_dashboard_authenticated(client, test_user, login):
    """
    GIVEN authenticated user
    WHEN the '/dashboard/' page is requested (GET)
    THEN check the page loads successfully and shows dashboard content
    """
    login(test_user)
    response = client.get(url_for("dashboard.index"))
    assert response.status_code == 200
    # Check for content indicative of the main dashboard page
    assert (
        b"Dashboard" in response.data
    )  # Assuming title in template 'dashboard/index.html'
    # Check for first name display (as per template logic)
    assert bytes(test_user.first_name, "utf-8") in response.data
