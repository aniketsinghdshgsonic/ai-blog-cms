"""
Routes for blog post management.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import db
from app.models.post import Post, PostStatus
from app.models.user import User, UserRole
from app.models.tag import Tag
from app.models.category import Category
from app.schemas.post import PostSchema, PostListSchema

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')
post_schema = PostSchema()
posts_schema = PostListSchema(many=True)


@posts_bp.route('', methods=['GET'])
def get_posts():
    """Get all published posts with filtering options."""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)  # Limit max per_page
    category = request.args.get('category')
    tag = request.args.get('tag')
    author = request.args.get('author')
    status = request.args.get('status', 'published')
    
    # Start with base query
    query = Post.query
    
    # Apply filters
    if category:
        category_obj = Category.query.filter_by(slug=category).first()
        if category_obj:
            query = query.filter_by(category_id=category_obj.id)
    
    if tag:
        tag_obj = Tag.query.filter_by(slug=tag).first()
        if tag_obj:
            query = query.join(Post.tags).filter(Tag.id == tag_obj.id)
    
    if author:
        author_obj = User.query.filter_by(username=author).first()
        if author_obj:
            query = query.filter_by(author_id=author_obj.id)
    
    # Apply status filter - non-admin users can only see published posts
    if status == 'published' or not request.headers.get('Authorization'):
        query = query.filter_by(status=PostStatus.PUBLISHED)
    elif status == 'all' and request.headers.get('Authorization'):
        # For authenticated requests, we'll check role in the route handler
        pass
    else:
        query = query.filter_by(status=PostStatus(status))
    
    # Sort by publication date (most recent first)
    query = query.order_by(Post.published_at.desc(), Post.created_at.desc())
    
    # Paginate results
    paginated_posts = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Return paginated results
    return jsonify({
        'posts': posts_schema.dump(paginated_posts.items),
        'pagination': {
            'total': paginated_posts.total,
            'pages': paginated_posts.pages,
            'page': paginated_posts.page,
            'per_page': paginated_posts.per_page,
            'has_next': paginated_posts.has_next,
            'has_prev': paginated_posts.has_prev
        }
    }), 200


@posts_bp.route('/<slug>', methods=['GET'])
def get_post(slug):
    """Get a single post by slug."""
    post = Post.query.filter_by(slug=slug).first()
    
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    # Check if post is published or user is authenticated
    if post.status != PostStatus.PUBLISHED and not request.headers.get('Authorization'):
        return jsonify({"error": "Post not found"}), 404
    
    # Increment view count
    post.increment_view()
    
    return jsonify(post_schema.dump(post)), 200


@posts_bp.route('', methods=['POST'])
@jwt_required()
def create_post():
    """Create a new post."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check if user has permission to create posts
    if user.role not in [UserRole.ADMIN, UserRole.EDITOR, UserRole.AUTHOR]:
        return jsonify({"error": "Permission denied"}), 403
    
    data = request.get_json()
    
    # Handle category
    category_id = None
    if 'category' in data:
        category = Category.query.filter_by(slug=data['category']).first()
        if category:
            category_id = category.id
    
    # Create post
    post = Post(
        title=data['title'],
        content=data['content'],
        author_id=user_id,
        category_id=category_id,
        summary=data.get('summary'),
        status=PostStatus(data.get('status', 'draft')),
        meta_title=data.get('meta_title'),
        meta_description=data.get('meta_description'),
        seo_keywords=data.get('seo_keywords'),
        featured_image=data.get('featured_image')
    )
    
    # Handle tags
    if 'tags' in data and isinstance(data['tags'], list):
        for tag_name in data['tags']:
            tag = Tag.find_or_create(tag_name)
            post.tags.append(tag)
    
    # Save post
    db.session.add(post)
    db.session.commit()
    
    return jsonify(post_schema.dump(post)), 201


@posts_bp.route('/<slug>', methods=['PUT'])
@jwt_required()
def update_post(slug):
    """Update an existing post."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    post = Post.query.filter_by(slug=slug).first()
    
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    # Check if user has permission to update this post
    if post.author_id != user_id and user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        return jsonify({"error": "Permission denied"}), 403
    
    data = request.get_json()
    
    # Update allowed fields
    allowed_fields = [
        'title', 'content', 'summary', 'featured_image',
        'meta_title', 'meta_description', 'seo_keywords'
    ]
    
    for field in allowed_fields:
        if field in data:
            setattr(post, field, data[field])
    
    # Handle special fields
    if 'status' in data:
        post.status = PostStatus(data['status'])
        if data['status'] == 'published' and not post.published_at:
            post.publish()
    
    # Handle category
    if 'category' in data:
        category = Category.query.filter_by(slug=data['category']).first()
        if category:
            post.category_id = category.id
        else:
            post.category_id = None
    
    # Handle tags
    if 'tags' in data and isinstance(data['tags'], list):
        # Clear existing tags
        post.tags = []
        # Add new tags
        for tag_name in data['tags']:
            tag = Tag.find_or_create(tag_name)
            post.tags.append(tag)
    
    db.session.commit()
    
    return jsonify(post_schema.dump(post)), 200


@posts_bp.route('/<slug>', methods=['DELETE'])
@jwt_required()
def delete_post(slug):
    """Delete a post."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    post = Post.query.filter_by(slug=slug).first()
    
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    # Check if user has permission to delete this post
    if post.author_id != user_id and user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        return jsonify({"error": "Permission denied"}), 403
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({"message": "Post deleted successfully"}), 200
