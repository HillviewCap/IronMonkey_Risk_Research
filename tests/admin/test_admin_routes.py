import pytest
from flask import url_for

def test_admin_dashboard_unauthenticated(client):
    """
    GIVEN unauthenticated user
    WHEN the '/admin/dashboard' page is requested (GET)
    THEN check it redirects to login
    """
    response = client.get(url_for('admin.dashboard'))
    from urllib.parse import urlparse, parse_qs

    assert response.status_code == 302

    # Parse the actual redirect location
    actual_location_parsed = urlparse(response.location)
    actual_query_params = parse_qs(actual_location_parsed.query)

    # Check the base path is the login URL
    assert actual_location_parsed.path == url_for('auth.login')

    # Check the 'next' parameter matches the expected admin dashboard URL
    assert 'next' in actual_query_params
    assert actual_query_params['next'][0] == url_for('admin.dashboard')

# TODO: Add test for non-admin authenticated user (should likely get 403 Forbidden)
# This requires checking if the route actually enforces admin privileges.
# def test_admin_dashboard_authenticated_non_admin(client, test_user, login):
#     """
#     GIVEN authenticated non-admin user
#     WHEN the '/admin/dashboard' page is requested (GET)
#     THEN check a 403 Forbidden response is returned
#     """
#     login(test_user)
#     response = client.get(url_for('admin.dashboard'))
#     assert response.status_code == 403

def test_admin_dashboard_authenticated_admin(client, admin_user, login):
    """
    GIVEN authenticated admin user
    WHEN the '/admin/dashboard' page is requested (GET)
    THEN check the page loads (or fails due to template)
    """
    login(admin_user) # Use the admin_user fixture
    response = client.get(url_for('admin.dashboard'))
    # Template exists now, expect 200 OK
    assert response.status_code == 200
    # assert b"Admin Dashboard" in response.data
    # Check for Jinja2 TemplateNotFound error in the response data (if DEBUG=True)


# --- User Management Placeholder Tests ---

# User List
def test_user_list_unauthenticated(client):
    """
    GIVEN unauthenticated user
    WHEN the '/admin/users' page is requested (GET)
    THEN check it redirects to login
    """
    response = client.get(url_for('admin.user_list'))
    assert response.status_code == 302 # Expect redirect to login

# TODO: Add test for non-admin authenticated user -> 403

def test_user_list_admin(client, admin_user, login):
    login(admin_user)
    response = client.get(url_for('admin.user_list'))
    assert response.status_code == 200 # Placeholder loads
    assert b"User List" in response.data # Assuming title in template

# User Detail
def test_user_detail_unauthenticated(client):
    response = client.get(url_for('admin.user_detail', user_id=1)) # Dummy ID
    assert response.status_code == 302

# TODO: Add test for non-admin authenticated user -> 403

def test_user_detail_admin(client, admin_user, login):
    login(admin_user)
    response = client.get(url_for('admin.user_detail', user_id=admin_user.id)) # Use admin's own ID
    assert response.status_code == 200 # Placeholder loads
    assert b"User Details" in response.data # Assuming title

def test_user_detail_admin_invalid_id(client, admin_user, login):
    login(admin_user)
    response = client.get(url_for('admin.user_detail', user_id=99999))
    assert response.status_code == 200 # Placeholder might not check ID yet, just loads template
    # If it did check ID and 404'd: assert response.status_code == 404

# User New (GET)
def test_user_new_get_unauthenticated(client):
    response = client.get(url_for('admin.user_new'))
    assert response.status_code == 302

# TODO: Add test for non-admin authenticated user -> 403

def test_user_new_get_admin(client, admin_user, login):
    login(admin_user)
    response = client.get(url_for('admin.user_new'))
    assert response.status_code == 200 # Placeholder loads
    assert b"New User" in response.data # Assuming title

# User New (POST) - Placeholder just renders template, so POST might not be handled yet
# def test_user_new_post_admin(client, admin_user, login):
#     login(admin_user)
#     response = client.post(url_for('admin.user_new'), data={...})
#     # Assert based on expected placeholder behavior (likely 200 or method not allowed 405)
#     assert response.status_code in [200, 405]

# User Edit (GET)
def test_user_edit_get_unauthenticated(client):
    response = client.get(url_for('admin.user_edit', user_id=1)) # Dummy ID


# --- System Logs Placeholder Tests ---
def test_system_logs_unauthenticated(client):
    response = client.get(url_for('admin.system_logs'))
    assert response.status_code == 302 # Expect redirect to login

# TODO: Add test for non-admin authenticated user -> 403

def test_system_logs_admin(client, admin_user, login):
    login(admin_user)
    response = client.get(url_for('admin.system_logs'))
    assert response.status_code == 200 # Placeholder loads
    assert b"System Logs" in response.data # Assuming title in template

# --- System Settings Placeholder Tests ---
def test_system_settings_unauthenticated(client):
    response = client.get(url_for('admin.system_settings'))
    assert response.status_code == 302 # Expect redirect to login

# TODO: Add test for non-admin authenticated user -> 403

def test_system_settings_admin(client, admin_user, login):
    login(admin_user)
    response = client.get(url_for('admin.system_settings'))
    assert response.status_code == 200 # Placeholder loads
    assert b"System Settings" in response.data # Assuming title in template
    # The previous assert was incorrect, should be 200
    # assert response.status_code == 302

# TODO: Add test for non-admin authenticated user -> 403

def test_user_edit_get_admin(client, admin_user, login):
    login(admin_user)
    response = client.get(url_for('admin.user_edit', user_id=admin_user.id))
    assert response.status_code == 200 # Placeholder loads
    assert b"Edit User" in response.data # Assuming title

def test_user_edit_get_admin_invalid_id(client, admin_user, login):
    login(admin_user)
    response = client.get(url_for('admin.user_edit', user_id=99999))
    # Now that the route uses get_or_404, expect 404 for invalid ID
    assert response.status_code == 404

# User Edit (POST) - Placeholder just renders template
# def test_user_edit_post_admin(client, admin_user, login):
#     login(admin_user)
#     response = client.post(url_for('admin.user_edit', user_id=admin_user.id), data={...})
#     # Assert based on expected placeholder behavior (likely 200 or 405)
#     assert response.status_code in [200, 405]

    # assert b"TemplateNotFound" in response.data
    # assert b"admin/dashboard.html" in response.data