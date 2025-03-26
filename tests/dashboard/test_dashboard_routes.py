import pytest
from flask import url_for

def test_dashboard_unauthenticated(client):
    """
    GIVEN unauthenticated user
    WHEN the '/dashboard/' page is requested (GET)
    THEN check it redirects to login
    """
    response = client.get(url_for('dashboard.index'))
    assert response.status_code == 302
    assert response.location == url_for('auth.login', _external=False)

def test_dashboard_authenticated(client, test_user, login):
    """
    GIVEN authenticated user
    WHEN the '/dashboard/' page is requested (GET)
    THEN check the page loads successfully and shows dashboard content
    """
    login(test_user)
    response = client.get(url_for('dashboard.index'))
    assert response.status_code == 200
    # Check for content indicative of the main dashboard page
    assert b"Dashboard" in response.data # Assuming title in template 'dashboard/index.html'
    # Check for username display (common on dashboards)
    assert bytes(test_user.username, 'utf-8') in response.data