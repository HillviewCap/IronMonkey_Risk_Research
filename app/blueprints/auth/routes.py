"""
Routes for authentication blueprint
"""

from sqlalchemy import text
import datetime
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    send_from_directory,
    current_app as app,
    session,
)
import os
from werkzeug.security import generate_password_hash  # For debug
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app.blueprints.auth import auth_bp
from app.models.user import User
from app import login_manager
from app.blueprints.auth.forms import RegistrationForm, LoginForm
from app.utils.db import get_db_connection, release_db_connection
from app import db  # Import db for session management


@auth_bp.route("/")
def index():
    return redirect(url_for("auth.login"))


@auth_bp.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            # Use SQLAlchemy ORM to find the user
            user = db.session.query(User).filter_by(username=form.username.data).first()

            if user:
                # DEBUGGING PASSWORD CHECK
                print(f"DEBUG: DB Hash for {user.username}: {user.password_hash}")
                password_check_result = user.check_password(form.password.data)
                print(
                    f"DEBUG: check_password('{form.password.data}') result: {password_check_result}"
                )
                # END DEBUGGING

                # Check password
                if not password_check_result:  # Check the result
                    flash("Invalid username or password", "danger")
                    return redirect(url_for("auth.login"))

                # Explicitly check if the user is active *before* attempting login
                # Handles cases where is_active might be None or False in the DB
                if not user.is_active:  # Checks for False or None
                    flash(
                        "Your account is inactive. Please contact support.", "warning"
                    )
                    return redirect(url_for("auth.login"))

                # Log successful login attempt (after password and active check)
                print(f"Login successful for active user: {user.username}")

                # Update last_login timestamp using SQLAlchemy session
                try:
                    # Use ORM approach for consistency if preferred, or keep text()
                    user.last_login = datetime.datetime.utcnow()
                    db.session.add(user)  # Add user to session if modified
                    # Commit will happen after successful login_user
                except Exception as e:
                    db.session.rollback()  # Rollback if last_login update fails
                    print(f"Failed to update last_login: {e}")
                    flash("An error occurred during login.", "danger")
                    return redirect(url_for("auth.login"))

                # Login user with Flask-Login - now we know user is active
                print(
                    f"DEBUG: User active status before login_user: {user.is_active}"
                )  # Should be True now
                login_successful = login_user(user, remember=form.remember_me.data)
                print(f"Login user result: {login_successful}")  # Should be True now

                if not login_successful:
                    # This case should ideally not happen now if user.is_active was True
                    flash("Login failed unexpectedly after active check.", "danger")
                    db.session.rollback()  # Rollback potential last_login change
                    return redirect(url_for("auth.login"))

                # Commit session changes including last_login update and Flask-Login session data
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f"Error committing session after login: {e}")
                    flash("An error occurred saving login state.", "danger")
                    # Log out the user manually as the session might be inconsistent
                    logout_user()
                    return redirect(url_for("auth.login"))

                next_page = request.args.get("next")
                if not next_page or url_parse(next_page).netloc != "":
                    next_page = url_for("dashboard.index")

                resp = redirect(next_page)
                # If in development environment, explicitly ensure cookies are not secure
                # Note: This cookie setting might be redundant if SESSION_COOKIE_SECURE is False in config
                if app.debug:
                    session_cookie_name = app.session_interface.get_cookie_name(app)
                    resp.set_cookie(
                        session_cookie_name,
                        request.cookies.get(session_cookie_name, ""),
                        httponly=True,
                        secure=False,
                    )  # Explicitly False for dev
                return resp
            else:  # Username not found
                flash("Invalid username or password", "danger")
                return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()  # Rollback on any exception during login process
            print(f"An error occurred during login: {e}")
            flash("An error occurred while logging in.", "danger")
            return redirect(url_for("auth.login"))
        # No finally block needed for db.session

    # GET request or form validation failed
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    session.clear()  # Explicitly clear session
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration"""
    print("Entering register route")
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User()
            user.username = form.username.data
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.set_password(form.password.data)  # This calculates password_hash

            # Set is_active explicitly to True for new registrations
            user.is_active = True

            # Use SQLAlchemy session for insertion
            current_time_utc = datetime.datetime.utcnow()  # Get current time
            result = db.session.execute(
                text(
                    """
                    INSERT INTO users.users_accounts
                    (username, email, password_hash, first_name, last_name, is_active, created_at)
                    VALUES (:username, :email, :password_hash, :first_name, :last_name, :is_active, :created_at)
                    RETURNING id
                """
                ),
                {
                    "username": user.username,
                    "email": user.email,
                    "password_hash": user.password_hash,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_active": user.is_active,  # Explicitly set to True
                    "created_at": current_time_utc,  # Add current timestamp
                },
            )
            user.id = result.scalar_one()  # Get the returned ID
            db.session.commit()

            flash("Congratulations, you are now a registered user!", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()  # Rollback on error
            print(f"An error occurred during registration: {e}")
            flash("An error occurred while registering.", "danger")
            # It's generally better to re-render the form on error than redirect
            # return redirect(url_for("auth.register"))
            return render_template("auth/register.html", form=form)
        # No manual connection release needed with db.session

    return render_template("auth/register.html", form=form)


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password_request():
    """Handle password reset request"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    # Placeholder for password reset logic
    return render_template("auth/reset_password_request.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Handle password reset with token"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    # Placeholder for password reset validation
    return render_template("auth/reset_password.html")


@auth_bp.route("/session-debug")
def session_debug():
    """Debug route to check session configuration"""
    from flask import session, jsonify
    import flask

    if current_user.is_authenticated:
        user_info = {
            "id": current_user.id,
            "username": current_user.username,
            "is_authenticated": current_user.is_authenticated,
        }
    else:
        user_info = {"is_authenticated": False, "message": "Not authenticated"}

    # Clean session data for display (remove sensitive info)
    session_data = {}
    for key in session:
        if key == "_user_id":  # Only show the user ID as it's useful for debugging
            session_data[key] = session[key]
        else:
            session_data[key] = "[HIDDEN]"

    debug_info = {
        "user": user_info,
        "session": session_data,
        "cookies": {k: "[HIDDEN]" for k in request.cookies},
        "cookie_names": list(request.cookies.keys()),
        "app_config": {
            "debug": app.debug,
            "testing": app.testing,
            "session_cookie_secure": app.config.get("SESSION_COOKIE_SECURE"),
            "remember_cookie_secure": app.config.get("REMEMBER_COOKIE_SECURE"),
            "session_cookie_httponly": app.config.get("SESSION_COOKIE_HTTPONLY"),
            "session_cookie_domain": app.config.get("SESSION_COOKIE_DOMAIN"),
            "session_cookie_path": app.config.get("SESSION_COOKIE_PATH", "/"),
            "session_type": app.config.get("SESSION_TYPE"),
        },
        "flask_version": flask.__version__,
    }

    return jsonify(debug_info)
