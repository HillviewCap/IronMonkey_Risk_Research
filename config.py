"""
Configuration settings for the IronMonkey Risk Research Platform
"""

import os
import urllib.parse
from datetime import timedelta


class Config:
    """Base configuration"""

    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Database settings
    clean_postgres_password = os.environ.get("POSTGRES_PASSWORD")
    if clean_postgres_password:
        clean_postgres_password = clean_postgres_password.strip("\"'")
    encoded_postgres_password = urllib.parse.quote_plus(clean_postgres_password)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"postgresql://{os.environ.get('POSTGRES_USER')}:{encoded_postgres_password}@{os.environ.get('POSTGRES_HOST')}:{os.environ.get('POSTGRES_PORT')}/{os.environ.get('POSTGRES_DB')}",
    )
    print(
        "Constructed SQLALCHEMY_DATABASE_URI (masked):",
        SQLALCHEMY_DATABASE_URI.replace(encoded_postgres_password, "****"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MongoDB settings
    MONGO_URI = os.environ.get(
        "MONGO_URI",
        f"mongodb://{os.environ.get('MONGO_USER')}:{os.environ.get('MONGO_PASSWORD')}@{os.environ.get('MONGO_HOST')}:{os.environ.get('MONGO_PORT')}/{os.environ.get('MONGO_DB')}",
    )

    # Elasticsearch settings
    ELASTICSEARCH_URL = os.environ.get(
        "ELASTICSEARCH_URL",
        f"http://{os.environ.get('ELASTICSEARCH_HOST')}:{os.environ.get('ELASTICSEARCH_PORT')}",
    )
    ELASTICSEARCH_PASSWORD = os.environ.get("ELASTICSEARCH_PASSWORD")

    # Redis settings
    REDIS_URL = os.environ.get(
        "REDIS_URL",
        f"redis://:{os.environ.get('REDIS_PASSWORD')}@{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/0",
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
    REMEMBER_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False


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
