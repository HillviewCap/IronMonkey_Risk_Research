import pytest
import json
from flask import url_for

# --- Calculate Score API Tests ---
def test_calculate_score_unauthenticated(client, test_assessment):
    """
    GIVEN unauthenticated user
    WHEN the '/api/assessments/<id>/calculate-score' endpoint is requested (POST)
    THEN check it redirects to login or returns 401
    """
    response = client.post(url_for('risk.calculate_assessment_score', assessment_id=test_assessment.id))
    # Assuming redirect for now
    assert response.status_code == 302
    assert response.location == url_for('auth.login', _external=False)
    # If 401: assert response.status_code == 401

def test_calculate_score_authenticated_invalid_status(client, test_user, login, test_assessment):
    """
    GIVEN authenticated user and an assessment not in 'review' or 'complete' status
    WHEN the '/api/assessments/<id>/calculate-score' endpoint is requested (POST)
    THEN check it returns a 400 Bad Request error
    """
    login(test_user)
    response = client.post(url_for('risk.calculate_assessment_score', assessment_id=test_assessment.id))
    assert response.status_code == 400
    assert response.content_type == 'application/json'
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Assessment must be in review or complete status' in data['message']

def test_calculate_score_authenticated_valid_status(client, test_user, login, test_assessment, db_session):
    """
    GIVEN authenticated user and an assessment in 'complete' status
    WHEN the '/api/assessments/<id>/calculate-score' endpoint is requested (POST)
    THEN check it returns a success response with score data
    """
    test_assessment.status = 'complete'
    db_session.add(test_assessment)
    db_session.commit()

    login(test_user)
    response = client.post(url_for('risk.calculate_assessment_score', assessment_id=test_assessment.id))
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'Assessment score calculated successfully' in data['message']
    assert 'data' in data
    assert data['data']['assessment_id'] == test_assessment.id
    assert 'overall_score' in data['data']
    assert 'framework_scores' in data['data']
    assert 'finding_scores' in data['data']

# --- Add Finding API Tests ---
def test_add_finding_unauthenticated(client, test_assessment):
    """
    GIVEN unauthenticated user
    WHEN the '/api/assessments/<id>/findings' endpoint is requested (POST)
    THEN check it redirects to login or returns 401
    """
    response = client.post(url_for('risk.add_finding', assessment_id=test_assessment.id), json={})
    # Assuming redirect for now
    assert response.status_code == 302
    assert response.location == url_for('auth.login', _external=False)
    # If 401: assert response.status_code == 401

def test_add_finding_authenticated_success(client, test_user, login, test_assessment, db_session):
    """
    GIVEN authenticated user and valid finding data
    WHEN the '/api/assessments/<id>/findings' endpoint is requested (POST)
    THEN check a new finding is created and success response is returned
    """
    login(test_user)
    finding_data = {
        'title': 'New API Finding',
        'description': 'Details about the finding.',
        'risk_level': 'High',
        'likelihood': 'Medium',
        'impact': 'Significant',
        'framework_category': 'Cyber Actor'
    }
    response = client.post(
        url_for('risk.add_finding', assessment_id=test_assessment.id),
        json=finding_data
    )
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'Finding added successfully' in data['message']
    assert 'data' in data
    assert 'finding_id' in data['data']
    new_finding_id = data['data']['finding_id']

    from app.models.risk import Finding
    new_finding = db_session.query(Finding).get(new_finding_id)
    assert new_finding is not None
    assert new_finding.assessment_id == test_assessment.id
    assert new_finding.title == finding_data['title']
    assert new_finding.risk_level == finding_data['risk_level']

def test_add_finding_authenticated_fail_validation(client, test_user, login, test_assessment):
    """
    GIVEN authenticated user and invalid finding data (missing required fields)
    WHEN the '/api/assessments/<id>/findings' endpoint is requested (POST)
    THEN check it returns a 400 Bad Request error
    """
    login(test_user)
    invalid_finding_data = {
        'description': 'Missing title and risk level'
        # Missing 'title', 'risk_level'
    }
    # --- RESTORED MISSING CODE ---
    response = client.post(
        url_for('risk.add_finding', assessment_id=test_assessment.id),
        json=invalid_finding_data
    )
    assert response.status_code == 400
    assert response.content_type == 'application/json'
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Missing required field' in data['message']
    # --- END RESTORED CODE ---

def test_add_finding_authenticated_invalid_assessment_id(client, test_user, login):
    """
    GIVEN authenticated user
    WHEN the '/api/assessments/<id>/findings' endpoint is requested (POST) with invalid assessment ID
    THEN check it returns 404 Not Found
    """
    login(test_user)
    invalid_id = 99999
    finding_data = {'title': 'Finding for invalid assessment', 'risk_level': 'Low'}
    response = client.post(
        url_for('risk.add_finding', assessment_id=invalid_id),
        json=finding_data
    )
    assert response.status_code == 404

# --- Add Recommendation API Tests ---
def test_add_recommendation_unauthenticated(client, test_finding):
    """
    GIVEN unauthenticated user
    WHEN the '/api/findings/<id>/recommendations' endpoint is requested (POST)
    THEN check it redirects to login or returns 401
    """
    response = client.post(url_for('risk.add_recommendation', finding_id=test_finding.id), json={})
    # Assuming redirect for now
    assert response.status_code == 302
    assert response.location == url_for('auth.login', _external=False)
    # If 401: assert response.status_code == 401

def test_add_recommendation_authenticated_success(client, test_user, login, test_finding, db_session):
    """
    GIVEN authenticated user and valid recommendation data for an existing finding
    WHEN the '/api/findings/<id>/recommendations' endpoint is requested (POST)
    THEN check a new recommendation is created and success response is returned
    """
    login(test_user)
    recommendation_data = {
        'title': 'New API Recommendation',
        'description': 'Details about the recommendation.',
        'priority': 'High',
        'implementation_cost': 'Medium',
        'implementation_time': 'Short'
    }
    response = client.post(
        url_for('risk.add_recommendation', finding_id=test_finding.id),
        json=recommendation_data
    )
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'Recommendation added successfully' in data['message']
    assert 'data' in data
    assert 'recommendation_id' in data['data']
    new_recommendation_id = data['data']['recommendation_id']

    from app.models.risk import Recommendation
    new_recommendation = db_session.query(Recommendation).get(new_recommendation_id)
    assert new_recommendation is not None
    assert new_recommendation.finding_id == test_finding.id
    assert new_recommendation.assessment_id == test_finding.assessment_id
    assert new_recommendation.title == recommendation_data['title']
    assert new_recommendation.priority == recommendation_data['priority']

def test_add_recommendation_authenticated_fail_validation(client, test_user, login, test_finding):
    """
    GIVEN authenticated user and invalid recommendation data (missing required fields)
    WHEN the '/api/findings/<id>/recommendations' endpoint is requested (POST)
    THEN check it returns a 400 Bad Request error
    """
    login(test_user)
    invalid_recommendation_data = {
        'description': 'Missing title and priority'
        # Missing 'title', 'priority'
    }
    response = client.post(
        url_for('risk.add_recommendation', finding_id=test_finding.id),
        json=invalid_recommendation_data
    )
    assert response.status_code == 400
    assert response.content_type == 'application/json'


# --- Report Generation API Tests ---
def test_generate_report_unauthenticated(client, test_assessment):
    """
    GIVEN unauthenticated user
    WHEN the '/api/assessments/<id>/report' endpoint is requested (GET)
    THEN check it redirects to login or returns 401
    """
    response = client.get(url_for('risk.generate_assessment_report_api', assessment_id=test_assessment.id))
    # Assuming redirect for now
    assert response.status_code == 302
    assert response.location == url_for('auth.login', _external=False)
    # If 401: assert response.status_code == 401

def test_generate_report_authenticated_html(client, test_user, login, test_assessment):
    """
    GIVEN authenticated user and a valid assessment
    WHEN the '/api/assessments/<id>/report' endpoint is requested (GET) with format=html
    THEN check it returns a successful HTML response
    """
    login(test_user)
    response = client.get(url_for('risk.generate_assessment_report_api', assessment_id=test_assessment.id, format='html'))
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    # Check for some basic HTML structure or content expected in the report
    assert b"<h1>Assessment Report</h1>" in response.data # Assuming this title exists in the report template
    assert bytes(test_assessment.name, 'utf-8') in response.data

def test_generate_report_authenticated_pdf(client, test_user, login, test_assessment):
    """
    GIVEN authenticated user and a valid assessment
    WHEN the '/api/assessments/<id>/report' endpoint is requested (GET) with format=pdf
    THEN check it returns a successful PDF response with correct headers
    """
    login(test_user)
    response = client.get(url_for('risk.generate_assessment_report_api', assessment_id=test_assessment.id, format='pdf'))
    assert response.status_code == 200
    assert response.content_type == 'application/pdf'
    # Check for the Content-Disposition header suggesting a download
    assert 'Content-Disposition' in response.headers
    assert f'attachment;filename=assessment_{test_assessment.id}_report.pdf' in response.headers['Content-Disposition']
    # Check if the response data looks like a PDF (starts with %PDF)
    assert response.data.startswith(b'%PDF')

def test_generate_report_authenticated_invalid_format(client, test_user, login, test_assessment):
    """
    GIVEN authenticated user and a valid assessment
    WHEN the '/api/assessments/<id>/report' endpoint is requested (GET) with an invalid format
    THEN check it returns a 400 Bad Request error
    """
    login(test_user)
    response = client.get(url_for('risk.generate_assessment_report_api', assessment_id=test_assessment.id, format='invalid'))
    assert response.status_code == 400
    assert response.content_type == 'application/json'
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Invalid report format requested' in data['message']

def test_generate_report_authenticated_invalid_assessment_id(client, test_user, login):
    """
    GIVEN authenticated user
    WHEN the '/api/assessments/<id>/report' endpoint is requested (GET) with invalid assessment ID
    THEN check it returns 404 Not Found
    """
    login(test_user)
    invalid_id = 99999
    response = client.get(url_for('risk.generate_assessment_report_api', assessment_id=invalid_id, format='html'))
    # The route uses get_or_404
    assert response.status_code == 404

    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Missing required field' in data['message']

def test_add_recommendation_authenticated_invalid_finding_id(client, test_user, login):
    """
    GIVEN authenticated user
    WHEN the '/api/findings/<id>/recommendations' endpoint is requested (POST) with invalid finding ID
    THEN check it returns 404 Not Found
    """
    login(test_user)
    invalid_id = 99999
    recommendation_data = {'title': 'Rec for invalid finding', 'priority': 'Low'}
    response = client.post(
        url_for('risk.add_recommendation', finding_id=invalid_id),
        json=recommendation_data
    )
    assert response.status_code == 404