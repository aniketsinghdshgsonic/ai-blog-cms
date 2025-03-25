"""
Database models package.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy and Migrate
db = SQLAlchemy()
migrate = Migrate()

# Import models to make them accessible from app.models
from app.models.user import User
from app.models.post import Post, PostStatus
from app.models.category import Category
from app.models.tag import Tag, post_tags
