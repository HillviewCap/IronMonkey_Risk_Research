"""
Routes for admin blueprint
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.blueprints.admin import admin_bp
from app.blueprints.admin.auth import admin_login_required
from app.models.user import User
from app import db # Ensure db is imported
from app.utils.db import get_db_connection, release_db_connection
from werkzeug.exceptions import NotFound

@admin_bp.route('/dashboard')
@admin_login_required
def dashboard():
    """Display admin dashboard"""
    return render_template('admin/dashboard.html')

@admin_bp.route('/users')
@admin_login_required
def user_list():
    """Display list of users"""
    # Placeholder for user list retrieval
    users = []
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>')
@admin_login_required
def user_detail(user_id):
    """Display user details"""
    # Placeholder for user detail retrieval
    user = None
    return render_template('admin/user_detail.html', user=user)

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@admin_login_required
def user_new():
    """Create new user"""
    # Placeholder for user creation logic
    return render_template('admin/user_edit.html', user=None)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_login_required
def user_edit(user_id):
    """Edit existing user"""
    conn = None
    user = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users.users_accounts WHERE id = %s", (user_id,))
            row = cur.fetchone()
            if row:
                user = User()
                user.id = row[0]
                user.username = row[1]
                user.email = row[2]
                user.password_hash = row[3] # Be careful exposing hash
                user.first_name = row[4]
                user.last_name = row[5]
                user.is_active = row[6]
                user.is_admin = row[7]
                user.created_at = row[8]
                user.last_login = row[9]
            else:
                # Raise 404 if user not found
                raise NotFound()
    except Exception as e:
        # Log the error appropriately
        print(f"Error fetching user {user_id} for edit: {e}")
        # Depending on desired behavior, could raise 500 or show error page
        raise # Re-raise for now, Flask will handle as 500
    finally:
        if conn:
            release_db_connection(conn)

    # TODO: Add POST logic for handling form submission
    return render_template('admin/user_edit.html', user=user)

@admin_bp.route('/logs')
@admin_login_required
def system_logs():
    """Display system logs"""
    # Placeholder for log retrieval
    logs = []
    return render_template('admin/logs.html', logs=logs)

@admin_bp.route('/settings')
@admin_login_required
def system_settings():
    """Display and edit system settings"""
    return render_template('admin/settings.html')
