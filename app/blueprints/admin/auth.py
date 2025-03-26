"""
Authentication utilities for admin blueprint
"""

from functools import wraps
from flask import redirect, url_for, current_app, request
from flask_login import current_user


def admin_login_required(f):
    """
    Custom decorator that enforces login requirement even in testing mode.
    This is needed because Flask-Login's login_required doesn't redirect
    when app.testing is True.

    This decorator mimics Flask-Login's login_required decorator by
    including the 'next' parameter in the redirect URL.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # Include the 'next' parameter in the redirect URL
            # Use request.path instead of request.url to get a relative URL
            return redirect(url_for("auth.login", next=request.path))
        return f(*args, **kwargs)

    return decorated_function
