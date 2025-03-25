"""
User model for authentication and authorization.
"""
import enum
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import db


class UserRole(enum.Enum):
    """Enum for user roles."""
    ADMIN = 'admin'
    EDITOR = 'editor'
    AUTHOR = 'author'
    READER = 'reader'


class User(db.Model):
    """User model for authentication and authorization."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.READER, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    posts = db.relationship('Post', back_populates='author', lazy='dynamic')

    def __init__(self, username, email, password, **kwargs):
        self.username = username
        self.email = email
        self.password = password
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def password(self):
        """Password property (getter)."""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Password property (setter)."""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Verify password."""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def is_admin(self):
        """Check if user is admin."""
        return self.role == UserRole.ADMIN

    def __repr__(self):
        return f'<User {self.username}>'
