"""
Category schemas for serialization and validation.
"""
from marshmallow import Schema, fields


class CategorySchema(Schema):
    """Category schema for detailed category information."""
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    slug = fields.String(dump_only=True)
    description = fields.String()
    parent_id = fields.Integer()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # SEO fields
    meta_title = fields.String()
    meta_description = fields.String()
    
    # Additional computed fields
    post_count = fields.Function(lambda obj: obj.post_count)
    has_children = fields.Function(lambda obj: obj.has_children)
    
    # For nested relationships
    parent = fields.Nested(
        'self',
        only=('id', 'name', 'slug'),
        dump_only=True,
        exclude=('parent',)
    )
    
    # Optional: Include subcategories (careful with circular references)
    subcategories = fields.Method('get_subcategories', dump_only=True)
    
    def get_subcategories(self, obj):
        """Get subcategories - only one level deep to avoid recursion issues."""
        if not obj.has_children:
            return []
        
        return CategorySchema(
            only=('id', 'name', 'slug', 'post_count'),
            many=True
        ).dump(obj.subcategories.all())
