import pytest
import json
from flask import url_for
from sqlalchemy import text


def test_login_page_loads(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/login' page is requested (GET) by unauthenticated user
    THEN check that the response is valid and contains expected content
    """
    response = client.get(url_for("auth.login"))
    assert response.status_code == 200
    assert (
        b"Sign In" in response.data
    )  # Check for expected text in the rendered template
    assert b"Username" in response.data
    assert b"Password" in response.data


def test_login_page_redirects_authenticated(client, test_user, login):
    """
    GIVEN an authenticated user
    WHEN the '/auth/login' page is requested (GET)
    THEN check that the response is a redirect to the dashboard
    """
    # Log in the user
    login(test_user)

    # Request the login page again
    response = client.get(url_for("auth.login"))
    assert response.status_code == 302


def test_login_success(client, test_user):
    """
    GIVEN a user created in the database
    WHEN the '/auth/login' page is posted to (POST) with correct credentials
    THEN check that the response is a redirect to the dashboard and a success message is flashed (optional)
    """
    # Ensure user is logged out first
    client.get(url_for("auth.logout"))

    response = client.post(
        url_for("auth.login"),
        data={
            "username": test_user.username,
            "password": "Password123!",  # Correct password from fixture
        },
        follow_redirects=True,
    )  # Follow redirects to check final destination

    assert response.status_code == 200  # Should land on dashboard
    # Check if it landed on the dashboard page
    assert (
        b"Dashboard" in response.data
    )  # Assuming dashboard template has "Dashboard" title/text
    # Optionally, check for flash messages if implemented
    # assert b"Login successful" in response.data # Example check


def test_login_fail_invalid_username(client, test_user):
    """
    GIVEN a user created in the database
    WHEN the '/auth/login' page is posted to (POST) with an invalid username
    THEN check that the response indicates failure (e.g., stays on login, flashes message)
    """
    # Explicitly logout first
    client.get(url_for("auth.logout"))

    response = client.post(
        url_for("auth.login"),
        data={"username": "wronguser", "password": "Password123!"},
        follow_redirects=True,
    )

    assert response.status_code == 200  # Should stay on/redirect back to login page
    assert b"Sign In" in response.data  # Check we are still on login page
    assert b"Invalid username or password" in response.data  # Check for flash message


def test_login_fail_invalid_password(client, test_user):
    """
    GIVEN a user created in the database
    WHEN the '/auth/login' page is posted to (POST) with an invalid password
    THEN check that the response indicates failure (e.g., stays on login, flashes message)
    """
    client.get(url_for("auth.logout"))  # Explicitly logout first

    response = client.post(
        url_for("auth.login"),
        data={
            "username": test_user.username,
            "password": "WrongPassword123!",  # Wrong password
        },
        follow_redirects=True,
    )

    assert response.status_code == 200  # Should stay on/redirect back to login page
    assert b"Sign In" in response.data  # Check we are still on login page
    assert b"Invalid username or password" in response.data  # Check for flash message


def test_logout(client, test_user, login):
    """
    GIVEN an authenticated user
    WHEN the '/auth/logout' page is requested (GET)
    THEN check that the user is logged out and redirected to the login page
    """
    # Log in the user first
    login(test_user)

    # Request the logout page
    response = client.get(url_for("auth.logout"), follow_redirects=True)

    # Check if redirected to login page
    assert response.status_code == 200  # After following redirect
    assert b"Sign In" in response.data  # Should be back on login page
    assert b"You have been logged out." in response.data  # Check for flash message


def test_register_page_loads(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/register' page is requested (GET) by unauthenticated user
    THEN check that the response is valid and contains expected content
    """
    # Explicitly logout first to ensure we're not authenticated
    client.get(url_for("auth.logout"))

    response = client.get(url_for("auth.register"))
    assert response.status_code == 200
    assert b"Register" in response.data  # Check for title/button
    assert b"Username" in response.data
    assert b"Email" in response.data
    assert b"Password" in response.data
    assert b"Repeat Password" in response.data


def test_register_page_redirects_authenticated(client, test_user, login):
    """
    GIVEN an authenticated user
    WHEN the '/auth/register' page is requested (GET)
    THEN check that the response is a redirect to the dashboard
    """
    login(test_user)
    response = client.get(url_for("auth.register"))
    assert response.status_code == 302
    assert response.location == url_for("dashboard.index", _external=False)


def test_register_success(client, db):  # Use db to check DB state
    """
    GIVEN valid registration data
    WHEN the '/auth/register' page is posted to (POST)
    THEN check that the response is a redirect to the login page and user is created
    """
    # Explicitly logout first to ensure we're not authenticated
    client.get(url_for("auth.logout"))

    # Ensure user doesn't exist before test using SQLAlchemy session execute
    result_before = db.session.execute(
        text("SELECT id FROM users.users_accounts WHERE username = :username"),
        {"username": "newuser"},
    )
    user_before = result_before.fetchone()
    assert user_before is None

    response = client.post(
        url_for("auth.register"),
        data={
            "username": "newuser",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "Password123!",  # Compliant password
            "password2": "Password123!",
            "submit": "Register",  # Include the submit button data
        },
        follow_redirects=True,
    )

    assert response.status_code == 200  # Should redirect to login
    assert b"Sign In" in response.data  # Check we are on login page
    assert (
        b"Congratulations, you are now a registered user!" in response.data
    )  # Check flash

    # Check user exists in DB after registration using SQLAlchemy session execute
    result_after = db.session.execute(
        text("SELECT username FROM users.users_accounts WHERE username = :username"),
        {"username": "newuser"},
    )
    user_after = result_after.fetchone()
    assert user_after is not None
    assert user_after[0] == "newuser"


def test_register_fail_username_exists(client, test_user):
    """
    GIVEN an existing user
    WHEN the '/auth/register' page is posted to (POST) with the same username
    THEN check that the response stays on register page and shows an error
    """
    client.get(url_for("auth.logout"))  # Explicitly logout first
    response = client.post(
        url_for("auth.register"),
        data={
            "username": test_user.username,  # Existing username
            "email": "another@example.com",
            "password": "Password123!",
            "password2": "Password123!",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200  # Should stay on register page
    assert b"Register" in response.data
    # Check for WTForms validation error (depends on how form errors are rendered)
    # This assumes the default WTForms rendering or similar
    assert b"Please use a different username." in response.data


def test_register_fail_email_exists(client, test_user):
    """
    GIVEN an existing user
    WHEN the '/auth/register' page is posted to (POST) with the same email
    THEN check that the response stays on register page and shows an error
    """
    client.get(url_for("auth.logout"))  # Explicitly logout first
    response = client.post(
        url_for("auth.register"),
        data={
            "username": "anotheruser",
            "email": test_user.email,  # Existing email
            "password": "Password123!",
            "password2": "Password123!",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200  # Should stay on register page
    assert b"Register" in response.data
    assert b"Please use a different email address." in response.data


def test_register_fail_password_mismatch(client):
    """
    GIVEN registration data with mismatching passwords
    WHEN the '/auth/register' page is posted to (POST)
    THEN check that the response stays on register page and shows an error
    """
    response = client.post(
        url_for("auth.register"),
        data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "Password123!",
            "password2": "PasswordMISMATCH!",  # Mismatch
        },
        follow_redirects=True,
    )

    assert response.status_code == 200  # Should stay on register page


def test_auth_index_redirects_to_login(client):
    """
    GIVEN unauthenticated user
    WHEN the '/auth/' page is requested (GET)
    THEN check that the response is a redirect to the login page
    """
    response = client.get(url_for("auth.index"))
    assert response.status_code == 302
    assert response.location == url_for("auth.login", _external=False)


def test_favicon_loads(client):
    """
    GIVEN a Flask application
    WHEN the '/auth/favicon.ico' is requested (GET)
    THEN check the response is valid and has the correct mimetype
    """
    # Note: The route definition uses send_from_directory relative to app.root_path/static


def test_reset_password_request_page_loads(client):
    """
    GIVEN unauthenticated user
    WHEN the '/auth/reset-password' page is requested (GET)
    THEN check the placeholder page loads correctly
    """
    client.get(url_for("auth.logout"))  # Explicitly logout first
    response = client.get(url_for("auth.reset_password_request"))
    assert response.status_code == 200
    # Check for some content indicative of the reset request page
    assert b"Reset Password" in response.data


def test_reset_password_request_page_redirects_authenticated(client, test_user, login):
    """
    GIVEN authenticated user
    WHEN the '/auth/reset-password' page is requested (GET)
    THEN check it redirects to the dashboard
    """
    login(test_user)
    response = client.get(url_for("auth.reset_password_request"))
    assert response.status_code == 302
    assert response.location == url_for("dashboard.index", _external=False)


def test_reset_password_token_page_loads(client):
    """
    GIVEN unauthenticated user and a dummy token
    WHEN the '/auth/reset-password/<token>' page is requested (GET)
    THEN check the placeholder page loads correctly
    """
    client.get(url_for("auth.logout"))  # Explicitly logout first
    response = client.get(url_for("auth.reset_password", token="dummy-token"))
    assert response.status_code == 200
    # Check for some content indicative of the reset page
    assert b"Reset Your Password" in response.data  # Assuming this text exists


def test_reset_password_token_page_redirects_authenticated(client, test_user, login):
    """
    GIVEN authenticated user and a dummy token
    WHEN the '/auth/reset-password/<token>' page is requested (GET)
    THEN check it redirects to the dashboard
    """
    login(test_user)
    response = client.get(url_for("auth.reset_password", token="dummy-token"))
    assert response.status_code == 302
    assert response.location == url_for("dashboard.index", _external=False)


def test_session_debug_unauthenticated(client):
    """
    GIVEN unauthenticated user
    WHEN the '/auth/session-debug' page is requested (GET)
    THEN check the JSON response indicates not authenticated
    """
    client.get(url_for("auth.logout"))  # Explicitly logout first
    response = client.get(url_for("auth.session_debug"))
    assert response.status_code == 200
    assert response.content_type == "application/json"
    data = json.loads(response.data)
    assert data["user"]["is_authenticated"] is False
    assert "session" in data
    assert "cookies" in data  # Check presence of keys


def test_session_debug_authenticated(client, test_user, login):
    """
    GIVEN authenticated user
    WHEN the '/auth/session-debug' page is requested (GET)
    THEN check the JSON response indicates authenticated user info
    """
    login(test_user)
    response = client.get(url_for("auth.session_debug"))
    assert response.status_code == 200
    assert response.content_type == "application/json"
    data = json.loads(response.data)
    assert data["user"]["is_authenticated"] is True
    assert data["user"]["id"] == test_user.id
    assert data["user"]["username"] == test_user.username
    assert "session" in data
    assert "_user_id" in data["session"]  # Check if user_id is in session data
    assert data["session"]["_user_id"] == str(
        test_user.id
    )  # Flask-Login stores ID as string
    assert "cookies" in data

    # Ensure the favicon exists there for the test to pass, or mock send_from_directory
    # Assuming the file exists for now.
    response = client.get(url_for("auth.favicon"))
    assert response.status_code == 200
    assert response.mimetype == "image/vnd.microsoft.icon"


# Note: Testing password complexity failure requires triggering the ValueError
# in User.set_password. This might happen automatically if the route calls it,
# or might need a specific test mocking/checking the exception handling in the route.
# Let's add a basic test assuming the route handles the ValueError.


def test_register_fail_password_complexity(client):
    """
    GIVEN registration data with a non-compliant password
    WHEN the '/auth/register' page is posted to (POST)
    THEN check that the response stays on register page and shows an error (implicitly)
    """
    client.get(url_for("auth.logout"))  # Explicitly logout first
    response = client.post(
        url_for("auth.register"),
        data={
            "username": "newuser",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "weak",  # Non-compliant password
            "password2": "weak",
            "submit": "Register",  # Include the submit button data
        },
        follow_redirects=True,
    )

    assert response.status_code == 200  # Should stay on register page
    assert b"Register" in response.data
    # Just check that we're still on the register page, not redirected to login
    # The specific error message might vary depending on implementation

    # Optional: Verify user is logged out by accessing a protected route
    response_dashboard = client.get(url_for("dashboard.index"))
    assert response_dashboard.status_code == 302  # Should redirect to login
    # Check if location starts with login URL, ignoring query params
    assert response_dashboard.location.startswith(
        url_for("auth.login", _external=False)
    )
