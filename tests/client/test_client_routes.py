import json
from flask import url_for

def test_client_search_page_unauthenticated(client):
    """
    GIVEN unauthenticated user
    WHEN the '/clients/search' page is requested (GET)
    THEN check it redirects to login
    """
    response = client.get(url_for('client.search_page'))
    assert response.status_code == 302
    assert response.location == url_for('auth.login', _external=False)

def test_client_search_page_authenticated(client, test_user, login):
    """
    GIVEN authenticated user
    WHEN the '/clients/search' page is requested (GET)
    THEN check the page loads successfully
    """
    login(test_user)
    response = client.get(url_for('client.search_page'))
    assert response.status_code == 200
    # Check for some content indicative of the client search page
    # Assuming the template 'client/search.html' contains this text


def test_client_search_api_unauthenticated(client):
    """
    GIVEN unauthenticated user
    WHEN the '/api/v1/clients/search' endpoint is requested (GET)
    THEN check it redirects to login (assuming standard Flask-Login behavior for APIs)
         or returns 401 Unauthorized if configured differently.
    """
    response = client.get(url_for('client.client_search'))
    # Check for redirect OR 401 depending on how API auth is handled
    # Flask-Login usually redirects HTML requests but might behave differently for API endpoints
    # depending on configuration or decorators used. Let's assume redirect for now.
    assert response.status_code == 302
    assert response.location == url_for('auth.login', _external=False)
    # If it should be 401, change the assertion:
    # assert response.status_code == 401

def test_client_search_api_authenticated_no_query(client, test_user, login):
    """
    GIVEN authenticated user
    WHEN the '/api/v1/clients/search' endpoint is requested (GET) with no query params
    THEN check the response is successful and returns expected JSON structure
    """
    login(test_user)
    response = client.get(url_for('client.client_search'))
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'data' in data
    assert isinstance(data['data'], list) # Expecting a list of results
    assert 'meta' in data
    assert 'total' in data['meta']

def test_client_search_api_authenticated_with_query(client, test_user, login):
    """
    GIVEN authenticated user
    WHEN the '/api/v1/clients/search' endpoint is requested (GET) with query params
    THEN check the response is successful and returns expected JSON structure
    """
    login(test_user)
    query_params = {'query': 'testcorp', 'industry': 'Tech', 'country': 'USA'}
    response = client.get(url_for('client.client_search', **query_params))
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'data' in data
    assert isinstance(data['data'], list)
    assert 'meta' in data
    # We can't easily assert the content of 'data' without knowing
    # what's in the dev Elasticsearch or mocking the service.
    # Checking the structure is a good start.

    assert b"Client Search" in response.data