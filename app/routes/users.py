"""
Routes for user management.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import db
from app.models.user import User, UserRole
from app.schemas.user import UserSchema, UserListSchema

users_bp = Blueprint('users', __name__, url_prefix='/users')
user_schema = UserSchema()
users_schema = UserListSchema(many=True)


@users_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (admin only)."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    # Only admins can list all users
    if current_user.role != UserRole.ADMIN:
        return jsonify({"error": "Permission denied"}), 403
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)  # Limit max per_page
    role = request.args.get('role')
    
    # Build query
    query = User.query
    
    # Apply filters
    if role:
        try:
            query = query.filter_by(role=UserRole(role))
        except ValueError:
            # Invalid role name, ignore filter
            pass
    
    # Order by username
    query = query.order_by(User.username)
    
    # Paginate results
    paginated_users = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Return paginated results
    return jsonify({
        'users': users_schema.dump(paginated_users.items),
        'pagination': {
            'total': paginated_users.total,
            'pages': paginated_users.pages,
            'page': paginated_users.page,
            'per_page': paginated_users.per_page,
            'has_next': paginated_users.has_next,
            'has_prev': paginated_users.has_prev
        }
    }), 200


@users_bp.route('/<username>', methods=['GET'])
@jwt_required()
def get_user(username):
    """Get a single user by username."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Users can view their own profile, admins can view any profile
    if current_user.id != user.id and current_user.role != UserRole.ADMIN:
        return jsonify({"error": "Permission denied"}), 403
    
    return jsonify(user_schema.dump(user)), 200


@users_bp.route('/<username>', methods=['PUT'])
@jwt_required()
def update_user(username):
    """Update a user (admin only or self)."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Users can update their own profile, admins can update any profile
    if current_user.id != user.id and current_user.role != UserRole.ADMIN:
        return jsonify({"error": "Permission denied"}), 403
    
    data = request.get_json()
    
    # Determine which fields can be updated based on role
    allowed_fields = ['first_name', 'last_name', 'bio', 'profile_image']
    
    # Admins can update additional fields
    if current_user.role == UserRole.ADMIN:
        allowed_fields.extend(['role', 'is_active'])
    
    # Update allowed fields
    for field in allowed_fields:
        if field in data:
            # Special handling for role field
            if field == 'role':
                try:
                    user.role = UserRole(data['role'])
                except ValueError:
                    return jsonify({"error": f"Invalid role: {data['role']}"}), 400
            else:
                setattr(user, field, data[field])
    
    # Handle email updates (requires unique check)
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already in use"}), 409
        user.email = data['email']
    
    # Handle username updates (requires unique check)
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already taken"}), 409
        user.username = data['username']
    
    # Handle password change
    if 'password' in data:
        # If user is changing their own password, require current password
        if current_user.id == user.id and 'current_password' not in data:
            return jsonify({"error": "Current password is required"}), 400
        
        # Verify current password for security (unless admin is changing someone else's password)
        if current_user.id == user.id and not current_user.verify_password(data.get('current_password')):
            return jsonify({"error": "Current password is incorrect"}), 401
        
        user.password = data['password']
    
    db.session.commit()
    
    return jsonify({
        "message": "User updated successfully",
        "user": user_schema.dump(user)
    }), 200


@users_bp.route('/<username>', methods=['DELETE'])
@jwt_required()
def delete_user(username):
    """Delete a user (admin only)."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    # Only admins can delete users
    if current_user.role != UserRole.ADMIN:
        return jsonify({"error": "Permission denied"}), 403
    
    # Prevent self-deletion for safety
    if current_user.username == username:
        return jsonify({"error": "Cannot delete your own account"}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # For safety, we might want to check if the user has content
    # and consider archiving instead of deleting
    if user.posts.count() > 0:
        return jsonify({
            "error": "User has published content. Consider deactivating instead of deleting."
        }), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message": "User deleted successfully"}), 200


@users_bp.route('/<username>/activate', methods=['PUT'])
@jwt_required()
def activate_user(username):
    """Activate a user account (admin only)."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    # Only admins can activate/deactivate users
    if current_user.role != UserRole.ADMIN:
        return jsonify({"error": "Permission denied"}), 403
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    user.is_active = True
    db.session.commit()
    
    return jsonify({
        "message": "User activated successfully",
        "user": user_schema.dump(user)
    }), 200


@users_bp.route('/<username>/deactivate', methods=['PUT'])
@jwt_required()
def deactivate_user(username):
    """Deactivate a user account (admin only)."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    # Only admins can activate/deactivate users
    if current_user.role != UserRole.ADMIN:
        return jsonify({"error": "Permission denied"}), 403
    
    # Prevent self-deactivation for safety
    if current_user.username == username:
        return jsonify({"error": "Cannot deactivate your own account"}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    user.is_active = False
    db.session.commit()
    
    return jsonify({
        "message": "User deactivated successfully",
        "user": user_schema.dump(user)
    }), 200
