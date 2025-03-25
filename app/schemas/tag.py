"""
Tag schemas for serialization and validation.
"""
from marshmallow import Schema, fields


class TagSchema(Schema):
    """Tag schema for detailed tag information."""
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    slug = fields.String(dump_only=True)
    description = fields.String()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Optional additional fields
    color = fields.String()  # HEX color code
    featured = fields.Boolean()
    
    # Additional computed fields
    post_count = fields.Function(lambda obj: obj.post_count)
