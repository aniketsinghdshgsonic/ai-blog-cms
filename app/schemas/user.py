"""
User schemas for serialization and validation.
"""
from marshmallow import Schema, fields, post_dump


class UserSchema(Schema):
    """User schema for detailed user information."""
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True)
    email = fields.Email(required=True)
    first_name = fields.String()
    last_name = fields.String()
    role = fields.String(attribute="role.value")
    bio = fields.String()
    profile_image = fields.String()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    last_login = fields.DateTime(dump_only=True)
    
    # Never expose password in responses
    password = fields.String(load_only=True)
    
    # Additional computed fields
    full_name = fields.Method("get_full_name")
    post_count = fields.Function(lambda obj: obj.posts.count())
    
    def get_full_name(self, obj):
        """Get user's full name."""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        elif obj.first_name:
            return obj.first_name
        elif obj.last_name:
            return obj.last_name
        return None


class UserListSchema(Schema):
    """User schema for list views with limited information."""
    id = fields.Integer(dump_only=True)
    username = fields.String()
    email = fields.Email()
    role = fields.String(attribute="role.value")
    profile_image = fields.String()
    is_active = fields.Boolean()
    full_name = fields.Method("get_full_name")
    
    def get_full_name(self, obj):
        """Get user's full name."""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        elif obj.first_name:
            return obj.first_name
        elif obj.last_name:
            return obj.last_name
        return None
