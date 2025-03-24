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
    WTF_CSRF_ENABLED = True  # Keep CSRF protection
    
    # Override base class settings for development
    def __init__(self):
        super().__init__()
        self.REMEMBER_COOKIE_SECURE = False
        self.SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres:postgres@localhost:5432/ironmonkey_test"
    )
    WTF_CSRF_ENABLED = False
    REMEMBER_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False


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
