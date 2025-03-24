"""
User model for authentication and authorization
"""
import re
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from app.utils.db import get_db_connection, release_db_connection

class User(UserMixin, db.Model):
    """User model for authentication and system access"""
    __tablename__ = 'users_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set user password hash, with complexity checks."""
        errors = []

        if len(password) < 8:
            errors.append("at least 8 characters")
        if not re.search("[A-Z]", password):
            errors.append("one uppercase letter")
        if not re.search("[a-z]", password):
            errors.append("one lowercase letter")
        if not re.search("[0-9]", password):
            errors.append("one number")
        if not re.search("[^A-Za-z0-9]", password):
            errors.append("one special character")

        if errors:
            error_message = "Password must contain: " + ", ".join(errors) + "."
            raise ValueError(error_message)

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

@staticmethod
def get_all_users():
    """Fetches all users from the database."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users_accounts")
            users = []
            for row in cur.fetchall():
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
                users.append(user.to_dict())
            return users
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []
    finally:
        if conn:
            release_db_connection(conn)
