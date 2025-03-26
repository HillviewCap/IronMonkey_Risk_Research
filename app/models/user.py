"""
User model for authentication and authorization
"""
import re
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
# Remove unused imports if User becomes a full SQLAlchemy model
# from sqlalchemy import text
# from app.utils.db import get_db_connection, release_db_connection

class User(UserMixin, db.Model): # Inherit from db.Model
    """User model for authentication and system access"""
    __tablename__ = 'users_accounts'
    __table_args__ = {'schema': 'users'} # Specify the schema

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    # Rename internal _is_active to is_active to match column name
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Flask-Login required methods are inherited or implicitly handled by UserMixin + SQLAlchemy

    # Keep __repr__
    def __repr__(self):
        return f'<User {self.username}>'

    # Keep password methods
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

    # Keep to_dict if needed for APIs
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
    """Load user by ID for Flask-Login using SQLAlchemy session"""
    print(f"Loading user with ID: {user_id}")
    
    # Handle potential non-integer IDs
    try:
        user_id = int(user_id)
    except (ValueError, TypeError): # Catch TypeError as well
        print(f"Invalid user_id format: {user_id}")
        return None
    
    try:
        # Use SQLAlchemy session to query the User model
        user = db.session.get(User, user_id) # Use Session.get for primary key lookup
        if user:
            print(f"User found via SQLAlchemy: ID={user.id}, Username={user.username}")
            return user
        else:
            print(f"No user found with ID: {user_id}")
            return None
    except Exception as e:
        print(f"Error in load_user (SQLAlchemy): {e}")
        import traceback
        traceback.print_exc()
        return None

# Remove get_all_users or adapt it to use SQLAlchemy if still needed
# @staticmethod
# def get_all_users():
#     """Fetches all users from the database."""
#     conn = None
#     try:
#         conn = get_db_connection()
#         with conn.cursor() as cur:
#             cur.execute("SELECT * FROM users.users_accounts")
#             users = []
#             for row in cur.fetchall():
#                 user = User()
#                 user.id = row[0]
#                 user.username = row[1]
#                 user.email = row[2]
#                 user.password_hash = row[3]
#                 user.first_name = row[4]
#                 user.last_name = row[5]
#                 user.is_active = row[6] # Changed from _is_active
#                 user.is_admin = row[7]
#                 user.created_at = row[8]
#                 user.last_login = row[9]
#                 users.append(user.to_dict())
#             return users
#     except Exception as e:
#         print(f"Error fetching users: {e}")
#         return []
#     finally:
#         if conn:
#             release_db_connection(conn)
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
            'is_active': self.is_active,  # This now uses the property
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
    
    try:
        # Use SQLAlchemy session to execute raw SQL
        result = db.session.execute(
            text("SELECT * FROM users.users_accounts WHERE id = :id"),
            {'id': user_id}
        )
        row = result.fetchone() # Fetch one row from the result proxy

        if row:
            print(f"User found via SQLAlchemy: ID={row[0]}, Username={row[1]}")
            user = User()
            # Map row columns to user attributes (assuming column order 0=id, 1=username, etc.)
            user.id = row[0]
            user.username = row[1]
            user.email = row[2]
            user.password_hash = row[3]
            user.first_name = row[4]
            user.last_name = row[5]
            user._is_active = row[6] # Use the backing field
            user.is_admin = row[7]
            user.created_at = row[8]
            user.last_login = row[9]
            return user
        else:
            print(f"No user found with ID: {user_id}")
            return None
    except Exception as e:
        print(f"Error in load_user (SQLAlchemy): {e}")
        import traceback
        traceback.print_exc()
        return None
    # No need for manual connection management; SQLAlchemy session handles it.

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
