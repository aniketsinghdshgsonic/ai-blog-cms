"""
Post schemas for serialization and validation.
"""
from marshmallow import Schema, fields, post_dump

from app.schemas.user import UserListSchema
from app.schemas.category import CategorySchema
from app.schemas.tag import TagSchema


class PostSchema(Schema):
    """Post schema for detailed post information."""
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    slug = fields.String(dump_only=True)
    content = fields.String(required=True)
    summary = fields.String()
    featured_image = fields.String()
    status = fields.String(attribute="status.value")
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    published_at = fields.DateTime(dump_only=True)
    
    # SEO fields
    meta_title = fields.String()
    meta_description = fields.String()
    seo_keywords = fields.String()
    
    # AI-related fields
    ai_generated = fields.Boolean()
    ai_prompts = fields.String()
    
    # Analytics
    view_count = fields.Integer(dump_only=True)
    share_count = fields.Integer(dump_only=True)
    
    # Relationships
    author_id = fields.Integer(required=True, load_only=True)
    author = fields.Nested(UserListSchema, dump_only=True)
    
    category_id = fields.Integer(load_only=True)
    category = fields.Nested(CategorySchema, dump_only=True)
    
    tags = fields.List(fields.Nested(TagSchema), dump_only=True)
    
    # For request handling
    category_slug = fields.String(load_only=True)
    tag_list = fields.List(fields.String(), load_only=True)
    
    # Additional computed fields
    reading_time = fields.Method("get_reading_time")
    excerpt = fields.Method("get_excerpt")
    
    def get_reading_time(self, obj):
        """Calculate approximate reading time in minutes."""
        word_count = len(obj.content.split())
        minutes = word_count / 200  # Average reading speed: 200 words per minute
        return max(1, round(minutes))
    
    def get_excerpt(self, obj):
        """Generate post excerpt."""
        return obj.generate_excerpt(length=150)


class PostListSchema(Schema):
    """Post schema for list views with limited information."""
    id = fields.Integer(dump_only=True)
    title = fields.String()
    slug = fields.String()
    summary = fields.String()
    featured_image = fields.String()
    status = fields.String(attribute="status.value")
    created_at = fields.DateTime()
    published_at = fields.DateTime()
    
    # Meta information
    meta_title = fields.String()
    
    # Relationships (limited information)
    author = fields.Nested(
        UserListSchema(only=("id", "username", "full_name", "profile_image")),
        dump_only=True
    )
    
    category = fields.Nested(
        CategorySchema(only=("id", "name", "slug")),
        dump_only=True
    )
    
    tags = fields.List(
        fields.Nested(TagSchema(only=("id", "name", "slug", "color"))),
        dump_only=True
    )
    
    # Additional computed fields
    reading_time = fields.Method("get_reading_time")
    excerpt = fields.Method("get_excerpt")
    
    def get_reading_time(self, obj):
        """Calculate approximate reading time in minutes."""
        word_count = len(obj.content.split())
        minutes = word_count / 200  # Average reading speed: 200 words per minute
        return max(1, round(minutes))
    
    def get_excerpt(self, obj):
        """Generate post excerpt."""
        return obj.generate_excerpt(length=150)
