"""
Routes for authentication blueprint
"""
from flask import render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app.blueprints.auth import auth_bp
from app.models.user import User
from app import login_manager
from app.blueprints.auth.forms import RegistrationForm, LoginForm
from app.utils.db import get_db_connection, release_db_connection


@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('client.dashboard'))

    form = LoginForm()
    conn = None  # Initialize conn
    if form.validate_on_submit():
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users_accounts WHERE username = %s", (form.username.data,))
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
                        flash('Invalid username or password', 'danger')
                        return redirect(url_for('auth.login'))
                    login_user(user, remember=form.remember_me.data)
                    next_page = request.args.get('next')
                    if not next_page or url_parse(next_page).netloc != '':
                        next_page = url_for('client.dashboard')
                    return redirect(next_page)
                else:
                    flash('Invalid username or password', 'danger')
                    return redirect(url_for('auth.login'))
        except Exception as e:
            print(f"An error occurred: {e}")
            flash('An error occurred while logging in.', 'danger')
            return redirect(url_for('auth.login'))
        finally:
            if conn:
                release_db_connection(conn)

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('client.dashboard'))

    form = RegistrationForm()
    conn = None  # Initialize conn
    if form.validate_on_submit():
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                user = User(username=form.username.data, email=form.email.data,
                            first_name=form.first_name.data, last_name=form.last_name.data)
                user.set_password(form.password.data)
                cur.execute(
                    "INSERT INTO users_accounts (username, email, password_hash, first_name, last_name) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (user.username, user.email, user.password_hash, user.first_name, user.last_name)
                )
                user.id = cur.fetchone()[0]
                conn.commit()
            flash('Congratulations, you are now a registered user!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(f"An error occurred: {e}")
            flash('An error occurred while registering.', 'danger')
            return redirect(url_for('auth.register'))
        finally:
            if conn:
                release_db_connection(conn)

    return render_template('auth/register.html', form=form)


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """Handle password reset request"""
    if current_user.is_authenticated:
        return redirect(url_for('client.dashboard'))

    # Placeholder for password reset logic
    return render_template('auth/reset_password_request.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token"""
    if current_user.is_authenticated:
        return redirect(url_for('client.dashboard'))

    # Placeholder for password reset validation
    return render_template('auth/reset_password.html')
