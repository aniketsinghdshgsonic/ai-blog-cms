"""
Authentication and authorization helper functions.
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.models.user import User, UserRole


def admin_required(fn):
    """
    Decorator to check if user is an admin.
    
    Args:
        fn: The function to decorate
        
    Returns:
        Function: Decorated function that checks admin permissions
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != UserRole.ADMIN:
            return jsonify({"error": "Admin privileges required"}), 403
        
        return fn(*args, **kwargs)
    
    return wrapper


def editor_required(fn):
    """
    Decorator to check if user is an editor or admin.
    
    Args:
        fn: The function to decorate
        
    Returns:
        Function: Decorated function that checks editor permissions
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
            return jsonify({"error": "Editor privileges required"}), 403
        
        return fn(*args, **kwargs)
    
    return wrapper


def author_required(fn):
    """
    Decorator to check if user is an author, editor, or admin.
    
    Args:
        fn: The function to decorate
        
    Returns:
        Function: Decorated function that checks author permissions
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in [UserRole.ADMIN, UserRole.EDITOR, UserRole.AUTHOR]:
            return jsonify({"error": "Author privileges required"}), 403
        
        return fn(*args, **kwargs)
    
    return wrapper


def check_post_ownership(user_id, post):
    """
    Check if user owns a post or has editor/admin rights.
    
    Args:
        user_id (int): User ID to check
        post (Post): Post object to check ownership for
        
    Returns:
        bool: True if user has permission to modify the post
    """
    user = User.query.get(user_id)
    
    # Post owner or admin/editor can modify
    if post.author_id == user_id or user.role in [UserRole.ADMIN, UserRole.EDITOR]:
        return True
    
    return False


def get_current_user():
    """
    Helper function to get the current authenticated user.
    
    Returns:
        User: Current authenticated user or None
    """
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    except:
        return None
