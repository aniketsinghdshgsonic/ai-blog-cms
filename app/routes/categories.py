"""
Routes for blog categories management.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import db
from app.models.category import Category
from app.models.user import User, UserRole
from app.schemas.category import CategorySchema

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)


@categories_bp.route('', methods=['GET'])
def get_categories():
    """Get all categories."""
    # Get query parameters
    parent_id = request.args.get('parent_id', type=int)
    
    # Build query
    query = Category.query
    
    # Filter by parent_id if provided
    if parent_id is not None:
        query = query.filter_by(parent_id=parent_id)
    
    # Order by name
    query = query.order_by(Category.name)
    
    # Execute query
    categories = query.all()
    
    return jsonify(categories_schema.dump(categories)), 200


@categories_bp.route('/<slug>', methods=['GET'])
def get_category(slug):
    """Get a single category by slug."""
    category = Category.query.filter_by(slug=slug).first()
    
    if not category:
        return jsonify({"error": "Category not found"}), 404
    
    return jsonify(category_schema.dump(category)), 200


@categories_bp.route('', methods=['POST'])
@jwt_required()
def create_category():
    """Create a new category."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check if user has permission to create categories
    if user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        return jsonify({"error": "Permission denied"}), 403
    
    data = request.get_json()
    
    # Check if category with same name already exists
    existing = Category.query.filter_by(name=data['name']).first()
    if existing:
        return jsonify({"error": "Category with this name already exists"}), 409
    
    # Handle parent category
    parent_id = None
    if 'parent_id' in data and data['parent_id']:
        parent = Category.query.get(data['parent_id'])
        if parent:
            parent_id = parent.id
    
    # Create category
    category = Category(
        name=data['name'],
        description=data.get('description'),
        parent_id=parent_id,
        meta_title=data.get('meta_title'),
        meta_description=data.get('meta_description')
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify(category_schema.dump(category)), 201


@categories_bp.route('/<slug>', methods=['PUT'])
@jwt_required()
def update_category(slug):
    """Update an existing category."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check if user has permission to update categories
    if user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        return jsonify({"error": "Permission denied"}), 403
    
    category = Category.query.filter_by(slug=slug).first()
    
    if not category:
        return jsonify({"error": "Category not found"}), 404
    
    data = request.get_json()
    
    # Check if changing name and if the new name already exists
    if 'name' in data and data['name'] != category.name:
        existing = Category.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({"error": "Category with this name already exists"}), 409
        category.name = data['name']
        category.slug = None  # Will be auto-generated
    
    # Update other fields
    if 'description' in data:
        category.description = data['description']
    
    if 'meta_title' in data:
        category.meta_title = data['meta_title']
    
    if 'meta_description' in data:
        category.meta_description = data['meta_description']
    
    # Handle parent category (check for circular references)
    if 'parent_id' in data:
        parent_id = data['parent_id']
        
        # Cannot make a category its own parent or child
        if parent_id == category.id:
            return jsonify({"error": "A category cannot be its own parent"}), 400
        
        # Check for deeper circular references
        if parent_id:
            parent = Category.query.get(parent_id)
            if not parent:
                return jsonify({"error": "Parent category not found"}), 404
                
            # Check if the new parent is a child of this category
            check_parent = parent
            while check_parent and check_parent.parent_id:
                if check_parent.parent_id == category.id:
                    return jsonify({"error": "Circular reference detected"}), 400
                check_parent = Category.query.get(check_parent.parent_id)
        
        category.parent_id = parent_id
    
    db.session.commit()
    
    return jsonify(category_schema.dump(category)), 200


@categories_bp.route('/<slug>', methods=['DELETE'])
@jwt_required()
def delete_category(slug):
    """Delete a category."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check if user has permission to delete categories
    if user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        return jsonify({"error": "Permission denied"}), 403
    
    category = Category.query.filter_by(slug=slug).first()
    
    if not category:
        return jsonify({"error": "Category not found"}), 404
    
    # Check if category has posts
    if category.posts.count() > 0:
        return jsonify({
            "error": "Cannot delete category with posts. Move posts to another category first."
        }), 400
    
    # Check if category has subcategories
    if category.subcategories.count() > 0:
        return jsonify({
            "error": "Cannot delete category with subcategories. Move or delete subcategories first."
        }), 400
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({"message": "Category deleted successfully"}), 200
