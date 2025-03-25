#!/bin/bash

# Make the script exit on any error
set -e

echo -e "\e[32mSetting up IronMonkey Risk Research Platform development environment...\e[0m"

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "\e[31mPlease activate your virtual environment first!\e[0m"
    echo "You can create and activate one with:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    exit 1
fi

# Install requirements
echo -e "\e[36mInstalling dependencies...\e[0m"
pip install -r requirements.txt

# Make sure Flask-Session is installed
echo -e "\e[36mEnsuring Flask-Session is installed...\e[0m"
pip install flask-session

# Make sure the script is executable
echo -e "\e[36mMaking start script executable...\e[0m"
chmod +x start_dev.sh

# Create session directory if it doesn't exist
if [ ! -d "flask_session" ]; then
    echo -e "\e[36mCreating session directory...\e[0m"
    mkdir -p flask_session
fi

echo -e "\e[32mSetup complete! You can now run the application with:\e[0m"
echo -e "\e[33m./start_dev.sh\e[0m"
