Write-Host "Setting up IronMonkey Risk Research Platform development environment..." -ForegroundColor Green

# Make sure we're in the virtual environment
if (-not ($env:VIRTUAL_ENV)) {
    Write-Host "Please activate your virtual environment first!" -ForegroundColor Red
    exit
}

# Install requirements
Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

# Make sure Flask-Session is installed
Write-Host "Ensuring Flask-Session is installed..." -ForegroundColor Cyan
pip install flask-session

Write-Host "Setup complete! You can now run the application with:" -ForegroundColor Green
Write-Host ".\start_dev.ps1" -ForegroundColor Yellow
