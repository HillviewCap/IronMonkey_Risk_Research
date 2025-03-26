import pytest
import os
import sys
import unittest.mock as mock
from flask.sessions import SessionInterface
from werkzeug.datastructures import CallbackDict
from flask import Flask
import redis
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from urllib.parse import urlparse

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import app BEFORE defining mock (or remove mock)
from app import create_app, db as _db  # Rename db to avoid conflict with fixture
from app.models.user import User  # Import User model - MOVED
from flask import url_for # Added for login fixture
from app.models.client import Client # Import Client model
from app.models.risk import Assessment, Finding, Recommendation # Import risk models
from datetime import date, timedelta # Import date/timedelta for assessment date
from werkzeug.security import generate_password_hash # MOVED

@pytest.fixture(scope='session') # Changed scope to session for app context
def app():
    """
    Creates a Flask application instance configured for testing.
    Scope is 'session' to ensure db setup/teardown happens once.
    """
    # Create app with testing config (which now includes test DB URIs)
    app = create_app('testing')
    # Ensure TESTING is explicitly True and CSRF is disabled for tests
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    # Use the actual Redis session interface configured in TestingConfig
    # app.session_interface = MockSessionInterface() # Removed this line
    app.config['LOGIN_DISABLED'] = False # Explicitly ensure login is NOT disabled for tests

    print(f"Using test database: {app.config['SQLALCHEMY_DATABASE_URI']}")

    app_context = app.app_context()
    app_context.push()

    yield app  # provide the app instance to the tests

    app_context.pop()

@pytest.fixture(scope='session')
def db(app):
    """
    Session-wide test database.
    Handles creation and dropping of the actual test database.
    """
    test_db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    parsed_uri = urlparse(test_db_uri)
    test_db_name = parsed_uri.path[1:] # Get db name like 'geopolitical_risk_test'

    # Construct URI for the default 'postgres' database to connect for creation/dropping
    default_db_uri = f"{parsed_uri.scheme}://{parsed_uri.netloc}/postgres"

    # Connect to the default database
    try:
        default_engine = create_engine(default_db_uri, isolation_level='AUTOCOMMIT')
        with default_engine.connect() as connection:
            print(f"Attempting to drop test database '{test_db_name}' if exists...")
            try:
                # Terminate connections before dropping
                connection.execute(text(f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{test_db_name}'
                      AND pid <> pg_backend_pid();
                """))
                connection.execute(text(f"DROP DATABASE {test_db_name}"))
                print(f"Dropped existing test database '{test_db_name}'.")
            except ProgrammingError as e:
                # Database doesn't exist or other error (e.g., permission)
                if "does not exist" in str(e):
                     print(f"Test database '{test_db_name}' does not exist, proceeding.")
                else:
                    print(f"Warning: Could not drop test database '{test_db_name}'. Error: {e}")
                    # Depending on the error, you might want to raise it
                    # raise # Uncomment to fail the test setup if drop fails unexpectedly

            print(f"Creating test database '{test_db_name}'...")
            connection.execute(text(f"CREATE DATABASE {test_db_name}"))
            print(f"Test database '{test_db_name}' created.")
    except Exception as e:
         pytest.fail(f"Failed to connect to default DB '{default_db_uri}' or manage test DB '{test_db_name}': {e}")
    finally:
        if 'default_engine' in locals():
            default_engine.dispose()


    # Now connect the app to the newly created test database
    _db.app = app
    # Don't call init_app again as it's already initialized in create_app
    # _db.init_app(app) # Ensure db is initialized with the app context

    # Ensure 'users' schema exists BEFORE creating tables
    print("Ensuring 'users' schema exists...")
    with _db.engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS users"))
        conn.commit() # Commit schema creation
    print("'users' schema ensured.")

    # Create tables within the test database (including users.users_accounts now)
    print(f"Creating tables in test database '{test_db_name}'...")
    _db.create_all()
    print("Tables created.") # Move this print statement here
    
    # Remove manual table creation for users_accounts as it's now handled by create_all()
    # print("Creating users schema and users_accounts table...")
    # with _db.engine.connect() as conn:
    #     # Schema creation moved before create_all()
    #     # conn.execute(text("CREATE SCHEMA IF NOT EXISTS users"))
    #     conn.execute(text("""
    #         CREATE TABLE IF NOT EXISTS users.users_accounts (
    #             id SERIAL PRIMARY KEY,
    #             username VARCHAR(255) UNIQUE NOT NULL,
    #             email VARCHAR(255) UNIQUE NOT NULL,
    #             password_hash VARCHAR(255) NOT NULL,
    #             first_name VARCHAR(255),
    #             last_name VARCHAR(255),
    #             is_active BOOLEAN DEFAULT TRUE,
    #             is_admin BOOLEAN DEFAULT FALSE,
    #             created_at TIMESTAMP DEFAULT NOW(),
    #             last_login TIMESTAMP
    #         )
    #     """))
    #     conn.commit() # This commit belongs to the removed block
    # print("Tables created.") # Moved earlier

    yield _db # provide the database instance for tests

    # --- Teardown ---
    print("Tearing down test database...")
    _db.session.remove() # Close the session used by tests

    # Connect to the default database again to drop the test database
    try:
        default_engine = create_engine(default_db_uri, isolation_level='AUTOCOMMIT')
        with default_engine.connect() as connection:
            print(f"Dropping test database '{test_db_name}'...")
             # Terminate connections before dropping
            connection.execute(text(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{test_db_name}'
                  AND pid <> pg_backend_pid();
            """))
            connection.execute(text(f"DROP DATABASE {test_db_name}"))
            print(f"Test database '{test_db_name}' dropped.")
    except Exception as e:
        print(f"Warning: Could not drop test database '{test_db_name}' during teardown. Error: {e}")
        # You might need manual cleanup
    finally:
        if 'default_engine' in locals():
            default_engine.dispose()


@pytest.fixture(scope='function') # Function scope for transaction rollback
def db_session(db):
    """
    Provides a transactional scope for tests.
    Provides the standard Flask-SQLAlchemy session with rollback.
    """
    yield db.session # Use the standard session provided by Flask-SQLAlchemy

    # Rollback any changes made during the test
    db.session.rollback()
    db.session.remove() # Ensure session is removed after rollback


@pytest.fixture(scope='function') # Change scope to function for client
def client(app):
    """
    Provides a Flask test client for making requests.
    """
    return app.test_client()

# Remove the authenticated_client fixture as it's no longer needed with real sessions
# @pytest.fixture(scope='function')
# def authenticated_client(app, test_user, monkeypatch):
#     """
#     Provides a Flask test client with an authenticated user by patching the LoginManager callback.
#     """
#     # Create a test client
#     client = app.test_client(use_cookies=True)
#
#     # Set up the session to include the user ID
#     with client.session_transaction() as sess:
#         sess['_user_id'] = str(test_user.id)
#         sess['_fresh'] = True
#
#     # Ensure the test_user object itself reports as authenticated
#     test_user.authenticated = True
#
#     # Patch the LoginManager's internal user callback
#     from app import login_manager
#
#     def mock_user_callback(user_id):
#         print(f"Mock LoginManager callback called with ID: {user_id}. Returning test_user.")
#         test_user.authenticated = True # Ensure it's marked authenticated
#         return test_user
#
#     # Patch the internal callback used by Flask-Login
#     monkeypatch.setattr(login_manager, '_user_callback', mock_user_callback)
#
#     return client

@pytest.fixture(scope='module') # Keep module scope for runner
def runner(app):
    """Provides a Flask CLI test runner."""
    return app.test_cli_runner() # RESTORED BODY


@pytest.fixture(scope='function')
def new_user(db_session): # Depend on db_session fixture for transactional scope
    """Factory fixture to create a new user within the test transaction."""
    created_users = [] # Keep track to return the object

    def _create_user(username, password, email, first_name="Test", last_name="User", is_admin=False, is_active=True):
        """Helper function to insert user data using the test session."""
        password_hash = generate_password_hash(password)
        try:
            result = db_session.execute(text("""
                INSERT INTO users.users_accounts
                (username, email, password_hash, first_name, last_name, is_admin, is_active, created_at)
                VALUES (:username, :email, :password_hash, :first_name, :last_name, :is_admin, :is_active, NOW())
                RETURNING id
                """),
                {
                    'username': username,
                    'email': email,
                    'password_hash': password_hash,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_admin': is_admin,
                    'is_active': is_active
                }
            )
            user_id = result.scalar_one() # Use scalar_one to ensure ID is returned
            db_session.flush() # Flush to ensure the user exists for immediate query if needed, commit happens later or via rollback
            print(f"Created user {username} (ID: {user_id}) within test transaction.")

            # Return a User object populated with data
            user = User()
            user.id = user_id
            user.username = username
            user.email = email
            user.password_hash = password_hash
            user.first_name = first_name
            user.last_name = last_name
            user.is_admin = is_admin
            user._is_active = is_active # Set the internal attribute
            created_users.append(user) # Store the created user object
            return user
        except Exception as e:
            print(f"Error creating user {username} within test transaction: {e}")
            db_session.rollback() # Rollback immediately on error during creation
            raise # Re-raise after logging

    yield _create_user

    # Cleanup is handled by the db_session fixture's rollback


@pytest.fixture(scope='function')
def test_user(db_session, new_user):
    """Creates a standard test user."""
    # Check if the user already exists
    result = db_session.execute(
        text("SELECT id FROM users.users_accounts WHERE username = :username"),
        {'username': 'testuser'}
    )
    existing_user = result.fetchone()
    
    if existing_user:
        # User already exists, create a User object with the existing data
        result = db_session.execute(
            text("SELECT * FROM users.users_accounts WHERE id = :id"),
            {'id': existing_user[0]}
        )
        row = result.fetchone()
        user = User()
        user.id = row[0]
        user.username = row[1]
        user.email = row[2]
        user.password_hash = row[3]
        user.first_name = row[4]
        user.last_name = row[5]
        user._is_active = row[6]
        user.is_admin = row[7]
        user.created_at = row[8]
        user.last_login = row[9]
        return user
    else:
        # User doesn't exist, create a new one
        return new_user(
            username='testuser',
            password='Password123!', # Compliant password
            email='test@example.com',
            is_admin=False
        )


@pytest.fixture(scope='function')
def login(client): # Removed monkeypatch as it wasn't helping here
    """Fixture to log in a user using the test client."""
    def _login(user, password='Password123!'):
        """Performs the login POST request without following redirects."""
        response = client.post(url_for('auth.login'), data={
            'username': user.username,
            'password': password,
            'submit': 'Sign In' # Add submit button data
        }, follow_redirects=False) # Set to False
        
        # Check if the POST request resulted in a redirect (302)
        assert response.status_code == 302, f"Login POST failed with status {response.status_code}"
        # Check if it redirects to the dashboard
        assert response.location == url_for('dashboard.index', _external=False), f"Login redirected to {response.location} instead of dashboard"
        
        # Optionally check for Set-Cookie header
        print(f"Login POST successful for user: {user.username}. Set-Cookie header present: {'session' in response.headers.get('Set-Cookie', '')}")
        
        return response # Return the redirect response
    return _login




@pytest.fixture(scope='function')
def new_client(db_session):
    """Factory fixture to create a new Client in the test database."""
    created_clients = []

    def _create_client(name="Test Client Inc.", industry="Technology", description="A test client.", website="http://example.com"):
        """Helper function to create and commit a Client instance."""
        client = Client(
            name=name,
            industry=industry,
            description=description,
            website=website
        )
        db_session.add(client)
        db_session.commit() # Commit within the nested transaction
        created_clients.append(client)
        return client

    yield _create_client

    # Cleanup is handled by db_session rollback


@pytest.fixture(scope='function')
def new_assessment(db_session):
    """Factory fixture to create a new Assessment in the test database."""
    created_assessments = []

    def _create_assessment(client_id, name="Test Assessment", assessment_date=None,
                           assessment_type="Full Framework", status="draft", assigned_user_id=None):
        """Helper function to create and commit an Assessment instance."""
        if assessment_date is None:
            assessment_date = date.today()

        assessment = Assessment(
            client_id=client_id,
            name=name,
            assessment_date=assessment_date,
            assessment_type=assessment_type,
            status=status,
            assigned_user_id=assigned_user_id
        )
        db_session.add(assessment)
        db_session.commit()
        created_assessments.append(assessment)
        return assessment

    yield _create_assessment
    # Cleanup handled by db_session rollback

@pytest.fixture(scope='function')
def test_assessment(new_assessment, test_client_instance, test_user):
    """Creates a standard test assessment linked to test_client and test_user."""
    return new_assessment(
        client_id=test_client_instance.id,
        assigned_user_id=test_user.id
    )

@pytest.fixture(scope='function')
def new_finding(db_session):
    """Factory fixture to create a new Finding in the test database."""
    created_findings = []

    def _create_finding(assessment_id, title="Test Finding", risk_level="Medium",
                        framework_category="Cyber Actor"):
        """Helper function to create and commit a Finding instance."""
        finding = Finding(
            assessment_id=assessment_id,
            title=title,
            risk_level=risk_level,
            framework_category=framework_category
        )
        db_session.add(finding)
        db_session.commit()
        created_findings.append(finding)
        return finding

    yield _create_finding
    # Cleanup handled by db_session rollback

@pytest.fixture(scope='function')
def test_finding(new_finding, test_assessment):
    """Creates a standard test finding linked to test_assessment."""
    return new_finding(assessment_id=test_assessment.id)

@pytest.fixture(scope='function')
def new_recommendation(db_session):
    """Factory fixture to create a new Recommendation in the test database."""
    created_recommendations = []

    def _create_recommendation(assessment_id, finding_id=None, title="Test Recommendation", priority="Medium"):
        """Helper function to create and commit a Recommendation instance."""
        recommendation = Recommendation(
            assessment_id=assessment_id,
            finding_id=finding_id,
            title=title,
            priority=priority
        )
        db_session.add(recommendation)
        db_session.commit()
        created_recommendations.append(recommendation)
        return recommendation

    yield _create_recommendation
    # Cleanup handled by db_session rollback

@pytest.fixture(scope='function')
def test_recommendation(new_recommendation, test_finding):
    """Creates a standard test recommendation linked to test_finding."""
    return new_recommendation(
        assessment_id=test_finding.assessment_id,
        finding_id=test_finding.id
    )


@pytest.fixture(scope='function')
def test_client_instance(new_client):
    """Creates a standard test client instance."""
    return new_client()

@pytest.fixture(scope='function')
def admin_user(db_session, new_user):
    """Creates an admin test user."""
    # Check if the user already exists
    result = db_session.execute(
        text("SELECT id FROM users.users_accounts WHERE username = :username"),
        {'username': 'adminuser'}
    )
    existing_user = result.fetchone()
    
    if existing_user:
        # User already exists, create a User object with the existing data
        result = db_session.execute(
            text("SELECT * FROM users.users_accounts WHERE id = :id"),
            {'id': existing_user[0]}
        )
        row = result.fetchone()
        user = User()
        user.id = row[0]
        user.username = row[1]
        user.email = row[2]
        user.password_hash = row[3]
        user.first_name = row[4]
        user.last_name = row[5]
        user._is_active = row[6]
        user.is_admin = row[7]
        user.created_at = row[8]
        user.last_login = row[9]
        return user
    else:
        # User doesn't exist, create a new one
        return new_user(
            username='adminuser',
            password='Password123!', # Compliant password
            email='admin@example.com',
            is_admin=True
        )


# --- Redis Fixtures ---

# Removed redis_client fixture as SESSION_REDIS is now configured in TestingConfig

@pytest.fixture(scope='function', autouse=True) # Auto-use to flush before each test
def redis_flush(app):
    """Flushes the Redis test database (DB 1) used by Flask-Session."""
    # Access the Redis client managed by Flask-Session
    redis_client = getattr(app.session_interface, 'redis', None) # Safely access redis client
    if redis_client:
        print("Flushing Redis test database (DB 1) via Flask-Session client...")
        try:
            redis_client.flushdb()
            print("Redis test database flushed.")
        except Exception as e:
            print(f"ERROR: Failed to flush Redis DB: {e}")
            # Fail the test immediately if Redis cannot be flushed
            pytest.fail(f"Failed to flush Redis DB: {e}")
    else:
        print("Skipping Redis flush: Flask-Session Redis client not available.")