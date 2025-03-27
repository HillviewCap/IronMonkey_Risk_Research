"""
Configuration settings for the IronMonkey Risk Research Platform
"""

import os
import urllib.parse
from datetime import timedelta


class Config:
    """Base configuration"""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-temporary-key-change-in-production")

    # Database settings
    clean_postgres_password = os.environ.get("POSTGRES_PASSWORD", "")
    if clean_postgres_password:
        clean_postgres_password = clean_postgres_password.strip("\"'")
    
    # Handle the case when password might be None
    encoded_postgres_password = urllib.parse.quote_plus(clean_postgres_password) if clean_postgres_password else ""
    
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"postgresql://{os.environ.get('POSTGRES_USER', 'postgres')}:{encoded_postgres_password}@{os.environ.get('POSTGRES_HOST', 'localhost')}:{os.environ.get('POSTGRES_PORT', '5432')}/{os.environ.get('POSTGRES_DB', 'geopolitical_risk')}",
    )
    print(
        "Constructed SQLALCHEMY_DATABASE_URI (masked):",
        SQLALCHEMY_DATABASE_URI.replace(encoded_postgres_password, "****") if encoded_postgres_password else SQLALCHEMY_DATABASE_URI,
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MongoDB settings
    mongo_password = os.environ.get("MONGO_PASSWORD", "")
    encoded_mongo_password = urllib.parse.quote_plus(mongo_password) if mongo_password else ""
    MONGO_URI = os.environ.get(
        "MONGO_URI",
        f"mongodb://{os.environ.get('MONGO_USER', '')}:{encoded_mongo_password}@{os.environ.get('MONGO_HOST', 'localhost')}:{os.environ.get('MONGO_PORT', '27017')}/{os.environ.get('MONGO_DB', 'ironmonkey')}",
    )

    # Elasticsearch settings
    ELASTICSEARCH_URL = os.environ.get(
        "ELASTICSEARCH_URL",
        f"http://{os.environ.get('ELASTICSEARCH_HOST', 'localhost')}:{os.environ.get('ELASTICSEARCH_PORT', '9200')}",
    )
    ELASTICSEARCH_PASSWORD = os.environ.get("ELASTICSEARCH_PASSWORD", "")

    # Redis settings
    redis_password = os.environ.get("REDIS_PASSWORD", "")
    encoded_redis_password = urllib.parse.quote_plus(redis_password) if redis_password else ""
    REDIS_URL = os.environ.get(
        "REDIS_URL",
        f"redis://:{encoded_redis_password}@{os.environ.get('REDIS_HOST', 'localhost')}:{os.environ.get('REDIS_PORT', '6379')}/0" if encoded_redis_password else f"redis://{os.environ.get('REDIS_HOST', 'localhost')}:{os.environ.get('REDIS_PORT', '6379')}/0",
    )

    # Session settings
    SESSION_TYPE = "redis"
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = "ironmonkey:"

    # Security settings
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    TESTING = False
    REMEMBER_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_DOMAIN = None  # Important for localhost
    SESSION_COOKIE_PATH = "/"
    WTF_CSRF_ENABLED = True  # Keep CSRF protection
    
    # Use filesystem sessions for development (more reliable than Redis)
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flask_session")
    SESSION_FILE_THRESHOLD = 500  # Maximum number of session files
    
    # Constructor to override settings
    def __init__(self):
        # Create session directory if it doesn't exist
        if not os.path.exists(self.SESSION_FILE_DIR):
            os.makedirs(self.SESSION_FILE_DIR)
            
        # Ensure these settings are applied
        self.DEBUG = True
        self.REMEMBER_COOKIE_SECURE = False
        self.SESSION_COOKIE_SECURE = False
        
        # Force settings from environment variables if present
        if os.environ.get('SESSION_COOKIE_SECURE') == 'False':
            print("Forcing SESSION_COOKIE_SECURE to False from environment")
            self.SESSION_COOKIE_SECURE = False
            
        if os.environ.get('REMEMBER_COOKIE_SECURE') == 'False':
            print("Forcing REMEMBER_COOKIE_SECURE to False from environment")
            self.REMEMBER_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    WTF_CSRF_ENABLED = False  # Disable CSRF for simpler testing
    REMEMBER_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    SESSION_TYPE = "redis" # Ensure tests use Redis for sessions if needed

    # Use env vars for connection, but specify dedicated test DB name/number
    # PostgreSQL Test DB
    clean_postgres_password = os.environ.get("POSTGRES_PASSWORD", "")
    if clean_postgres_password:
        clean_postgres_password = clean_postgres_password.strip("\"'")
    encoded_postgres_password = urllib.parse.quote_plus(clean_postgres_password) if clean_postgres_password else ""
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.environ.get('POSTGRES_USER', 'postgres')}:{encoded_postgres_password}@{os.environ.get('POSTGRES_HOST', 'localhost')}:{os.environ.get('POSTGRES_PORT', '5432')}/geopolitical_risk_test" # Test DB name

    # --- Redis Test DB (using DB 1) ---
    # Define REDIS_URL at class level for TestingConfig
    _base_redis_url_env = os.environ.get("REDIS_URL")
    _redis_password = os.environ.get("REDIS_PASSWORD", "")
    print(f"TestingConfig DEBUG: Base REDIS_URL from env: {_base_redis_url_env}")
    print(f"TestingConfig DEBUG: REDIS_PASSWORD available: {'Yes' if _redis_password else 'No'}")
    
    if _base_redis_url_env:
        try:
            _parsed_redis = urllib.parse.urlparse(_base_redis_url_env)
            # Check if password is in the URL
            has_password_in_url = '@' in _parsed_redis.netloc
            print(f"TestingConfig DEBUG: Password in URL netloc: {has_password_in_url}")
            
            # If password not in URL but available in env, reconstruct netloc with password
            if not has_password_in_url and _redis_password:
                _encoded_redis_password = urllib.parse.quote_plus(_redis_password)
                # Extract host:port from netloc
                if ':' in _parsed_redis.netloc:
                    _host_port = _parsed_redis.netloc
                    _new_netloc = f":{_encoded_redis_password}@{_host_port}"
                else:
                    _new_netloc = f":{_encoded_redis_password}@{_parsed_redis.netloc}"
                
                # Reconstruct URL with password and DB 1
                REDIS_URL = urllib.parse.urlunparse(
                    (_parsed_redis.scheme, _new_netloc, '/1', '', '', '')
                )
            else:
                # Just change the DB number to 1
                REDIS_URL = urllib.parse.urlunparse(
                    (_parsed_redis.scheme, _parsed_redis.netloc, '/1', '', '', '')
                )
            
            print(f"TestingConfig: Constructed REDIS_URL from env: {REDIS_URL}")
        except Exception as e:
            print(f"TestingConfig Warning: Failed to parse REDIS_URL '{_base_redis_url_env}'. Falling back. Error: {e}")
            # Fallback logic
            _redis_host = os.environ.get('REDIS_HOST', 'localhost')
            _redis_port = os.environ.get('REDIS_PORT', '6379')
            _encoded_redis_password = urllib.parse.quote_plus(_redis_password) if _redis_password else ""
            REDIS_URL = f"redis://:{_encoded_redis_password}@{_redis_host}:{_redis_port}/1" if _encoded_redis_password else f"redis://{_redis_host}:{_redis_port}/1"
            print(f"TestingConfig: Constructed REDIS_URL from fallback components: {REDIS_URL}")
    else:
        # Fallback if REDIS_URL is not set
        _redis_host = os.environ.get('REDIS_HOST', 'localhost')
        _redis_port = os.environ.get('REDIS_PORT', '6379')
        _encoded_redis_password = urllib.parse.quote_plus(_redis_password) if _redis_password else ""
        REDIS_URL = f"redis://:{_encoded_redis_password}@{_redis_host}:{_redis_port}/1" if _encoded_redis_password else f"redis://{_redis_host}:{_redis_port}/1"
        print(f"TestingConfig: Constructed REDIS_URL from components (REDIS_URL env var not found): {REDIS_URL}")
    # Clean up temporary variables used for class-level construction
    del _base_redis_url_env
    if '_parsed_redis' in locals(): del _parsed_redis
    if '_redis_host' in locals(): del _redis_host
    if '_redis_port' in locals(): del _redis_port
    if '_redis_password' in locals(): del _redis_password
    if '_encoded_redis_password' in locals(): del _encoded_redis_password
    
    # --- Configure Flask-Session ---
    try:
        import redis
        SESSION_REDIS = redis.from_url(REDIS_URL)
        print(f"TestingConfig: SESSION_REDIS configured using URL: {REDIS_URL}")
    except ImportError:
        print("TestingConfig Warning: redis package not installed. Cannot configure SESSION_REDIS.")
        SESSION_REDIS = None
    except Exception as e:
        print(f"TestingConfig Warning: Failed to create SESSION_REDIS from URL '{REDIS_URL}'. Error: {e}")
        SESSION_REDIS = None
    # --- End Redis Test DB ---


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    TESTING = False
    # Production settings should use environment variables for security


# Dictionary for config selection
config_dict = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

app_env = os.environ.get("APP_ENV", "default")
config = config_dict.get(app_env, DevelopmentConfig)
