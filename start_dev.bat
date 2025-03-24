@echo off
echo Starting IronMonkey Risk Research Platform in development mode...

set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_DEBUG=1
set APP_ENV=development
set SESSION_COOKIE_SECURE=False
set REMEMBER_COOKIE_SECURE=False

echo Environment variables set:
echo FLASK_APP=%FLASK_APP%
echo FLASK_ENV=%FLASK_ENV%
echo FLASK_DEBUG=%FLASK_DEBUG%
echo APP_ENV=%APP_ENV%
echo SESSION_COOKIE_SECURE=%SESSION_COOKIE_SECURE%
echo REMEMBER_COOKIE_SECURE=%REMEMBER_COOKIE_SECURE%

echo.
echo Starting Flask application...
python -m flask run --host=0.0.0.0 --port=5050 --debug
