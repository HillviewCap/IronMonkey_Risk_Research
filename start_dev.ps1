Write-Host "Starting IronMonkey Risk Research Platform in development mode..." -ForegroundColor Green

# Set environment variables
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
$env:FLASK_DEBUG = "1"
$env:APP_ENV = "development"
$env:SESSION_COOKIE_SECURE = "False"
$env:REMEMBER_COOKIE_SECURE = "False"

Write-Host "Environment variables set:" -ForegroundColor Cyan
Write-Host "FLASK_APP: $env:FLASK_APP"
Write-Host "FLASK_ENV: $env:FLASK_ENV"
Write-Host "FLASK_DEBUG: $env:FLASK_DEBUG"
Write-Host "APP_ENV: $env:APP_ENV"
Write-Host "SESSION_COOKIE_SECURE: $env:SESSION_COOKIE_SECURE"
Write-Host "REMEMBER_COOKIE_SECURE: $env:REMEMBER_COOKIE_SECURE"

Write-Host ""
Write-Host "Starting Flask application..." -ForegroundColor Yellow
python -m flask run --host=0.0.0.0 --port=5050 --debug
