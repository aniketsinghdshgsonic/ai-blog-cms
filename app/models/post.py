"""
Post model for blog articles.
"""
import enum
from datetime import datetime
import re
from slugify import slugify

from app.models import db


class PostStatus(enum.Enum):
    """Enum for post status."""
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'


class Post(db.Model):
    """Post model for blog articles."""
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500), nullable=True)
    featured_image = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Enum(PostStatus), default=PostStatus.DRAFT, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    
    # SEO fields
    meta_title = db.Column(db.String(200), nullable=True)
    meta_description = db.Column(db.String(300), nullable=True)
    seo_keywords = db.Column(db.String(300), nullable=True)
    
    # AI-related fields
    ai_generated = db.Column(db.Boolean, default=False)
    ai_prompts = db.Column(db.Text, nullable=True)
    
    # Analytics
    view_count = db.Column(db.Integer, default=0)
    share_count = db.Column(db.Integer, default=0)
    
    # Relationships
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User', back_populates='posts')
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.relationship('Category', back_populates='posts')
    
    tags = db.relationship('Tag', secondary='post_tags', backref=db.backref('posts', lazy='dynamic'))
    
    def __init__(self, title, content, author_id, **kwargs):
        self.title = title
        self.content = content
        self.author_id = author_id
        self.slug = slugify(title)
        
        # Set default values for SEO fields if not provided
        if 'meta_title' not in kwargs:
            self.meta_title = title
            
        if 'meta_description' not in kwargs and 'summary' in kwargs:
            self.meta_description = kwargs['summary']
        
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def publish(self):
        """Publish a post."""
        self.status = PostStatus.PUBLISHED
        self.published_at = datetime.utcnow()
        db.session.commit()
    
    def archive(self):
        """Archive a post."""
        self.status = PostStatus.ARCHIVED
        db.session.commit()
    
    def increment_view(self):
        """Increment view count."""
        self.view_count += 1
        db.session.commit()
    
    def increment_share(self):
        """Increment share count."""
        self.share_count += 1
        db.session.commit()
    
    def generate_excerpt(self, length=150):
        """Generate post excerpt by stripping HTML and truncating."""
        # Simple HTML tag removal - in production you might want a more robust solution
        text = re.sub(r'<[^>]+>', '', self.content)
        return text[:length] + '...' if len(text) > length else text
    
    def __repr__(self):
        return f'<Post {self.title}>'
