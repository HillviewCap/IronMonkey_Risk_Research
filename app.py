"""
IronMonkey Risk Research Platform
Main application entry point
"""
import os
import sys
from app import create_app
from dotenv import load_dotenv

load_dotenv()

# Force debug mode
os.environ['APP_ENV'] = 'development'
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'
os.environ['FLASK_APP'] = 'app.py'
# Force non-secure cookie settings for development
os.environ['SESSION_COOKIE_SECURE'] = 'False'
os.environ['REMEMBER_COOKIE_SECURE'] = 'False'

print("Python version:", sys.version)
print("Environment variables:")
print(f"APP_ENV: {os.environ.get('APP_ENV')}")
print(f"FLASK_ENV: {os.environ.get('FLASK_ENV')}")
print(f"FLASK_DEBUG: {os.environ.get('FLASK_DEBUG')}")
print(f"SESSION_COOKIE_SECURE: {os.environ.get('SESSION_COOKIE_SECURE')}")

# Create app with explicit development config
app = create_app('development')

# Debug settings
print(f"Debug mode: {app.debug}")
print(f"Testing mode: {app.testing}")
print(f"Session cookie secure: {app.config.get('SESSION_COOKIE_SECURE')}")
print(f"Remember cookie secure: {app.config.get('REMEMBER_COOKIE_SECURE')}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)  # Changed port to 5050
