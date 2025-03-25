"""
Category model for organizing blog posts.
"""
from datetime import datetime
from slugify import slugify

from app.models import db


class Category(db.Model):
    """Category model for organizing blog posts."""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # SEO fields
    meta_title = db.Column(db.String(200), nullable=True)
    meta_description = db.Column(db.String(300), nullable=True)
    
    # Relationships
    posts = db.relationship('Post', back_populates='category', lazy='dynamic')
    subcategories = db.relationship(
        'Category',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic'
    )
    
    def __init__(self, name, **kwargs):
        self.name = name
        self.slug = slugify(name)
        
        # Set default values for SEO fields if not provided
        if 'meta_title' not in kwargs:
            self.meta_title = name
            
        if 'meta_description' not in kwargs and 'description' in kwargs:
            self.meta_description = kwargs['description']
        
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @property
    def post_count(self):
        """Get the number of posts in this category."""
        return self.posts.count()
    
    @property
    def has_children(self):
        """Check if category has subcategories."""
        return self.subcategories.count() > 0
    
    def __repr__(self):
        return f'<Category {self.name}>'
