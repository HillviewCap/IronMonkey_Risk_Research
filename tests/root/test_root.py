from flask import url_for

def test_root_redirect_unauthenticated(client):
    """
    GIVEN an unauthenticated user
    WHEN the '/' page is requested (GET)
    THEN check that the response is a redirect to the login page
    """
    from flask_login import current_user
    print(f"DEBUG - Before request: current_user.is_authenticated = {current_user.is_authenticated}")
    
    response = client.get('/')
    print(f"DEBUG - Response status: {response.status_code}, location: {response.location}")
    print(f"DEBUG - Expected location: {url_for('auth.login', _external=False)}")
    
    assert response.status_code == 302
    # Use url_for with _external=False for relative path comparison
    assert response.location == url_for('auth.login', _external=False)

def test_root_redirect_authenticated(client, test_user, login):
    """
    GIVEN an authenticated user
    WHEN the '/' page is requested (GET)
    THEN check that the response is a redirect to the dashboard page
    """
    # Log in the user using the login fixture
    login(test_user)

    # Now request the root path
    response = client.get('/')
    print(f"Response status: {response.status_code}, location: {response.location}")
    
    # Check the response
    assert response.status_code == 302
    assert response.location == url_for('dashboard.index', _external=False)