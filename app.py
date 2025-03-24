"""
IronMonkey Risk Research Platform
Main application entry point
"""
import os
from app import create_app
from dotenv import load_dotenv

load_dotenv()

# Ensure we're running in development mode
os.environ['APP_ENV'] = 'development'
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

# Create app with explicit development config
app = create_app('development')

# Debug settings
print(f"Debug mode: {app.debug}")
print(f"Testing mode: {app.testing}")
print(f"Session cookie secure: {app.config.get('SESSION_COOKIE_SECURE')}")
print(f"Remember cookie secure: {app.config.get('REMEMBER_COOKIE_SECURE')}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
