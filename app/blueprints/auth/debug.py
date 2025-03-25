"""
Debugging routes for authentication and session issues
"""
from flask import jsonify, session, request, current_app
from flask_login import current_user
import os
import sys
import datetime

def register_debug_routes(bp):
    """Register debugging routes with the auth blueprint"""
    
    @bp.route("/debug")
    def debug_info():
        """Return detailed debugging information"""
        
        # Python and environment info
        env_info = {
            "python_version": sys.version,
            "platform": sys.platform,
            "env_vars": {
                key: value for key, value in os.environ.items() 
                if key.startswith(("FLASK_", "SESSION_", "APP_", "REMEMBER_"))
            }
        }
        
        # Flask configuration
        app_config = {
            "debug": current_app.debug,
            "testing": current_app.testing,
            "secret_key_set": bool(current_app.config.get("SECRET_KEY")),
            "session_type": current_app.config.get("SESSION_TYPE"),
            "session_cookie_secure": current_app.config.get("SESSION_COOKIE_SECURE"),
            "remember_cookie_secure": current_app.config.get("REMEMBER_COOKIE_SECURE"),
            "permanent_session_lifetime": str(current_app.config.get("PERMANENT_SESSION_LIFETIME")),
            "SERVER_NAME": current_app.config.get("SERVER_NAME"),
            "APPLICATION_ROOT": current_app.config.get("APPLICATION_ROOT"),
            "PREFERRED_URL_SCHEME": current_app.config.get("PREFERRED_URL_SCHEME"),
        }
        
        # User information
        if current_user.is_authenticated:
            user_info = {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "is_active": current_user.is_active,
                "is_authenticated": current_user.is_authenticated,
                "is_anonymous": current_user.is_anonymous,
            }
        else:
            user_info = {
                "is_authenticated": False,
                "is_anonymous": current_user.is_anonymous,
                "message": "Not authenticated"
            }
        
        # Session information
        session_info = {
            "id": session.sid if hasattr(session, "sid") else None,
            "modified": session.modified if hasattr(session, "modified") else None,
            "new": session.new if hasattr(session, "new") else None,
            "keys": list(session.keys()) if session else [],
            "_user_id": session.get("_user_id"),
            "_id": id(session),
        }
        
        # Request information
        request_info = {
            "cookies": {k: v for k, v in request.cookies.items()},
            "headers": {k: v for k, v in request.headers.items()},
            "user_agent": request.user_agent.string,
            "remote_addr": request.remote_addr,
            "method": request.method,
            "path": request.path,
            "url": request.url,
        }
        
        # Extensions and imports
        extensions_info = {
            "login_manager": str(current_app.extensions.get("login_manager")),
            "session_interface": str(current_app.session_interface),
            "redis": hasattr(current_app, "redis"),
            "elasticsearch": hasattr(current_app, "elasticsearch"),
        }
        
        return jsonify({
            "timestamp": datetime.datetime.now().isoformat(),
            "environment": env_info,
            "application": app_config,
            "user": user_info,
            "session": session_info,
            "request": request_info,
            "extensions": extensions_info,
        })
