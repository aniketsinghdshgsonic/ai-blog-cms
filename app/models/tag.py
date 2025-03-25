"""
Tag model and post_tags association table for blog post tagging.
"""
from datetime import datetime
from slugify import slugify

from app.models import db


# Association table for many-to-many relationship between posts and tags
post_tags = db.Table(
    'post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class Tag(db.Model):
    """Tag model for categorizing blog posts."""
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(60), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Optional additional fields
    color = db.Column(db.String(7), nullable=True)  # HEX color code
    featured = db.Column(db.Boolean, default=False)  # Highlighted tags
    
    def __init__(self, name, **kwargs):
        self.name = name
        self.slug = slugify(name)
        
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @property
    def post_count(self):
        """Get the number of posts with this tag."""
        return self.posts.count()
    
    @classmethod
    def find_or_create(cls, name):
        """Find an existing tag or create a new one."""
        slug = slugify(name)
        existing = cls.query.filter_by(slug=slug).first()
        
        if existing:
            return existing
        
        new_tag = cls(name=name)
        db.session.add(new_tag)
        db.session.commit()
        return new_tag
    
    def __repr__(self):
        return f'<Tag {self.name}>'
