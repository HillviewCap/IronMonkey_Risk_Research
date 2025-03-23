"""
Configuration settings for the IronMonkey Risk Research Platform
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/ironmonkey')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Elasticsearch settings
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200')
    
    # Redis settings
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Session settings
    SESSION_TYPE = 'redis'
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
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/ironmonkey_test'
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
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
