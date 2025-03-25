"""
Authentication routes for user management.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)

from app.models import db
from app.models.user import User
from app.schemas.user import UserSchema

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
user_schema = UserSchema()


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    # Check if user already exists
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"error": "Email already registered"}), 409
    
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"error": "Username already taken"}), 409
    
    # Create new user
    try:
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            "message": "User registered successfully",
            "user": user_schema.dump(user),
            "access_token": access_token
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a user."""
    data = request.get_json()
    
    # Find user by email or username
    user = User.query.filter_by(email=data.get('email')).first() or \
           User.query.filter_by(username=data.get('email')).first()
    
    if not user or not user.verify_password(data.get('password')):
        return jsonify({"error": "Invalid credentials"}), 401
    
    if not user.is_active:
        return jsonify({"error": "Account is deactivated"}), 403
    
    # Update last login
    user.update_last_login()
    
    # Generate token
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        "message": "Login successful",
        "user": user_schema.dump(user),
        "access_token": access_token
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get current user profile."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user_schema.dump(user)), 200


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """Update current user profile."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    allowed_fields = ['first_name', 'last_name', 'bio', 'profile_image']
    
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])
    
    # Handle password change separately for security
    if 'password' in data and data.get('current_password'):
        if not user.verify_password(data.get('current_password')):
            return jsonify({"error": "Current password is incorrect"}), 400
        user.password = data['password']
    
    db.session.commit()
    
    return jsonify({
        "message": "Profile updated successfully",
        "user": user_schema.dump(user)
    }), 200
