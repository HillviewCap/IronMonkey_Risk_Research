"""
Routes for authentication blueprint
"""

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    send_from_directory,
    current_app as app,
)
import os
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app.blueprints.auth import auth_bp
from app.models.user import User
from app import login_manager
from app.blueprints.auth.forms import RegistrationForm, LoginForm
from app.utils.db import get_db_connection, release_db_connection


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
    conn = None  # Initialize conn
    if form.validate_on_submit():
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM users.users_accounts WHERE username = %s",
                    (form.username.data,),
                )
                row = cur.fetchone()
                if row:
                    user = User()
                    user.id = row[0]
                    user.username = row[1]
                    user.email = row[2]
                    user.password_hash = row[3]
                    user.first_name = row[4]
                    user.last_name = row[5]
                    user.is_active = row[6]
                    user.is_admin = row[7]
                    user.created_at = row[8]
                    user.last_login = row[9]

                    if user is None or not user.check_password(form.password.data):
                        flash("Invalid username or password", "danger")
                        return redirect(url_for("auth.login"))
                    # Log successful login attempt
                    print(f"Login successful for user: {user.username}")
                    
                    # Update last_login timestamp
                    try:
                        with conn.cursor() as update_cur:
                            update_cur.execute(
                                "UPDATE users.users_accounts SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                                (user.id,)
                            )
                            conn.commit()
                    except Exception as e:
                        print(f"Failed to update last_login: {e}")
                        
                    # Set authentication flag
                    user.authenticated = True
                    
                    # Login user with Flask-Login
                    result = login_user(user, remember=form.remember_me.data)
                    
                    # Debug: Check if user is authenticated after login_user
                    print(f"Login user result: {result}")
                    print(f"User authenticated after login_user: {current_user.is_authenticated}")
                    
                    # Force session to save immediately
                    from flask import session
                    session['_user_id'] = user.get_id()
                    session.modified = True
                    
                    next_page = request.args.get("next")
                    if not next_page or url_parse(next_page).netloc != "":
                        next_page = url_for("dashboard.index")
                    
                    resp = redirect(next_page)
                    # If in development environment, explicitly ensure cookies are not secure
                    if app.debug:
                        session_cookie_name = app.session_interface.get_cookie_name(app)
                        resp.set_cookie(session_cookie_name, 
                                        request.cookies.get(session_cookie_name, ''),
                                        httponly=True, 
                                        secure=False)
                    return resp
                else:
                    flash("Invalid username or password", "danger")
                    return redirect(url_for("auth.login"))
        except Exception as e:
            print(f"An error occurred: {e}")
            flash("An error occurred while logging in.", "danger")
            return redirect(url_for("auth.login"))
        finally:
            if conn:
                release_db_connection(conn)

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration"""
    print("Entering register route")
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegistrationForm()
    conn = None  # Initialize conn
    if form.validate_on_submit():
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                user = User(
                    username=form.username.data,
                    email=form.email.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                )
                user.set_password(form.password.data)
                cur.execute(
                    "INSERT INTO users.users_accounts (username, email, password_hash, first_name, last_name) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (
                        user.username,
                        user.email,
                        user.password_hash,
                        user.first_name,
                        user.last_name,
                    ),
                )
                user.id = cur.fetchone()[0]
                conn.commit()
            flash("Congratulations, you are now a registered user!", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            print(f"An error occurred: {e}")
            flash("An error occurred while registering.", "danger")
            return redirect(url_for("auth.register"))
        finally:
            if conn:
                release_db_connection(conn)

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
            'id': current_user.id,
            'username': current_user.username,
            'is_authenticated': current_user.is_authenticated,
        }
    else:
        user_info = {
            'is_authenticated': False,
            'message': 'Not authenticated'
        }
    
    # Clean session data for display (remove sensitive info)
    session_data = {}
    for key in session:
        if key == '_user_id':  # Only show the user ID as it's useful for debugging
            session_data[key] = session[key]
        else:
            session_data[key] = '[HIDDEN]'
    
    debug_info = {
        'user': user_info,
        'session': session_data,
        'cookies': {k: '[HIDDEN]' for k in request.cookies},
        'cookie_names': list(request.cookies.keys()),
        'app_config': {
            'debug': app.debug,
            'testing': app.testing,
            'session_cookie_secure': app.config.get('SESSION_COOKIE_SECURE'),
            'remember_cookie_secure': app.config.get('REMEMBER_COOKIE_SECURE'),
            'session_cookie_httponly': app.config.get('SESSION_COOKIE_HTTPONLY'),
            'session_cookie_domain': app.config.get('SESSION_COOKIE_DOMAIN'),
            'session_cookie_path': app.config.get('SESSION_COOKIE_PATH', '/'),
            'session_type': app.config.get('SESSION_TYPE'),
        },
        'flask_version': flask.__version__,
    }
    
    return jsonify(debug_info)
