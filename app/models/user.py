"""
User model for authentication and authorization
"""
import re
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from app.utils.db import get_db_connection, release_db_connection

class User(UserMixin):
    """User model for authentication and system access"""
    # We're not fully using SQLAlchemy here, so customize for direct DB use
    
    def __init__(self):
        self.id = None
        self.username = None
        self.email = None
        self.password_hash = None
        self.first_name = None
        self.last_name = None
        self.is_active = True
        self.is_admin = False
        self.created_at = None
        self.last_login = None
        self.authenticated = False
    
    # Add Flask-Login required methods
    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return self.authenticated
    
    def is_active(self):
        return self.is_active
    
    def is_anonymous(self):
        return False
    
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

# Move loader function outside class to avoid method resolution issues
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    print(f"Loading user with ID: {user_id}")
    
    # Handle potential non-integer IDs
    try:
        user_id = int(user_id)
    except ValueError:
        print(f"Invalid user_id format: {user_id}")
        return None
    
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            query = "SELECT * FROM users.users_accounts WHERE id = %s"
            print(f"Executing query: {query} with id: {user_id}")
            cur.execute(query, (user_id,))
            row = cur.fetchone()
            
            if row:
                print(f"User found: ID={row[0]}, Username={row[1]}")
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
                
                # This is critical for Flask-Login to recognize authenticated users
                user.authenticated = True
                
                return user
            else:
                print(f"No user found with ID: {user_id}")
                return None
    except Exception as e:
        print(f"Error in load_user: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if conn:
            release_db_connection(conn)

@staticmethod
def get_all_users():
    """Fetches all users from the database."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users.users_accounts")
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
