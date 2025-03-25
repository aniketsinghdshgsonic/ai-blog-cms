"""
Routes for blog tags management.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import db
from app.models.tag import Tag
from app.models.user import User, UserRole
from app.schemas.tag import TagSchema

tags_bp = Blueprint('tags', __name__, url_prefix='/tags')
tag_schema = TagSchema()
tags_schema = TagSchema(many=True)


@tags_bp.route('', methods=['GET'])
def get_tags():
    """Get all tags."""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)  # Limit max per_page
    sort_by = request.args.get('sort_by', 'name')  # name or post_count
    featured = request.args.get('featured', type=bool)
    
    # Build query
    query = Tag.query
    
    # Apply filters
    if featured is not None:
        query = query.filter_by(featured=featured)
    
    # Apply sorting
    if sort_by == 'post_count':
        # This is a bit more complex as it involves a subquery
        # For simplicity, we'll fetch all and sort in Python
        tags = query.all()
        tags.sort(key=lambda x: x.post_count, reverse=True)
        
        # Manual pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_tags = tags[start:end]
        
        return jsonify({
            'tags': tags_schema.dump(paginated_tags),
            'pagination': {
                'total': len(tags),
                'pages': (len(tags) + per_page - 1) // per_page,
                'page': page,
                'per_page': per_page
            }
        }), 200
    else:
        # Sort by name (default)
        query = query.order_by(Tag.name)
        
        # Paginate results
        paginated_tags = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Return paginated results
        return jsonify({
            'tags': tags_schema.dump(paginated_tags.items),
            'pagination': {
                'total': paginated_tags.total,
                'pages': paginated_tags.pages,
                'page': paginated_tags.page,
                'per_page': paginated_tags.per_page,
                'has_next': paginated_tags.has_next,
                'has_prev': paginated_tags.has_prev
            }
        }), 200


@tags_bp.route('/<slug>', methods=['GET'])
def get_tag(slug):
    """Get a single tag by slug."""
    tag = Tag.query.filter_by(slug=slug).first()
    
    if not tag:
        return jsonify({"error": "Tag not found"}), 404
    
    return jsonify(tag_schema.dump(tag)), 200


@tags_bp.route('', methods=['POST'])
@jwt_required()
def create_tag():
    """Create a new tag."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check if user has permission to create tags
    if user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        return jsonify({"error": "Permission denied"}), 403
    
    data = request.get_json()
    
    # Check if tag with same name already exists
    existing = Tag.query.filter_by(name=data['name']).first()
    if existing:
        return jsonify({"error": "Tag with this name already exists"}), 409
    
    # Create tag
    tag = Tag(
        name=data['name'],
        description=data.get('description'),
        color=data.get('color'),
        featured=data.get('featured', False)
    )
    
    db.session.add(tag)
    db.session.commit()
    
    return jsonify(tag_schema.dump(tag)), 201


@tags_bp.route('/<slug>', methods=['PUT'])
@jwt_required()
def update_tag(slug):
    """Update an existing tag."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check if user has permission to update tags
    if user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        return jsonify({"error": "Permission denied"}), 403
    
    tag = Tag.query.filter_by(slug=slug).first()
    
    if not tag:
        return jsonify({"error": "Tag not found"}), 404
    
    data = request.get_json()
    
    # Check if changing name and if the new name already exists
    if 'name' in data and data['name'] != tag.name:
        existing = Tag.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({"error": "Tag with this name already exists"}), 409
        tag.name = data['name']
        tag.slug = None  # Will be auto-generated
    
    # Update other fields
    if 'description' in data:
        tag.description = data['description']
    
    if 'color' in data:
        tag.color = data['color']
    
    if 'featured' in data:
        tag.featured = data['featured']
    
    db.session.commit()
    
    return jsonify(tag_schema.dump(tag)), 200


@tags_bp.route('/<slug>', methods=['DELETE'])
@jwt_required()
def delete_tag(slug):
    """Delete a tag."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check if user has permission to delete tags
    if user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        return jsonify({"error": "Permission denied"}), 403
    
    tag = Tag.query.filter_by(slug=slug).first()
    
    if not tag:
        return jsonify({"error": "Tag not found"}), 404
    
    # Note: We don't need to check if tag has posts because we're using a many-to-many
    # relationship, so deleting a tag doesn't affect post records
    
    db.session.delete(tag)
    db.session.commit()
    
    return jsonify({"message": "Tag deleted successfully"}), 200
