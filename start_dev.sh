#!/bin/bash

# Make the script exit on any error
set -e

echo -e "\e[32mStarting IronMonkey Risk Research Platform in development mode...\e[0m"

# Set environment variables
export FLASK_APP="app.py"
export FLASK_ENV="development"
export FLASK_DEBUG="1"
export APP_ENV="development"
export SESSION_COOKIE_SECURE="False"
export REMEMBER_COOKIE_SECURE="False"

# Display environment variables
echo -e "\e[36mEnvironment variables set:\e[0m"
echo "FLASK_APP: $FLASK_APP"
echo "FLASK_ENV: $FLASK_ENV"
echo "FLASK_DEBUG: $FLASK_DEBUG"
echo "APP_ENV: $APP_ENV"
echo "SESSION_COOKIE_SECURE: $SESSION_COOKIE_SECURE"
echo "REMEMBER_COOKIE_SECURE: $REMEMBER_COOKIE_SECURE"

echo ""
echo -e "\e[33mStarting Flask application...\e[0m"
python -m flask run --host=0.0.0.0 --port=5050 --debug
