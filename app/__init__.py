"""
Flask application factory.
"""
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger

from app.config import config_by_name

# Import models - needed for Flask-Migrate to detect them
from app.models import db, migrate


def create_app(config_name=None):
    """
    Flask application factory.
    
    Args:
        config_name: Configuration name (development, production, testing)
    
    Returns:
        Configured Flask application
    """
    if not config_name:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)
    
    # Initialize Swagger
    swagger_config = {
        "headers": [],
        "specs": [{
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs"
    }
    Swagger(app, config=swagger_config)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.posts import posts_bp
    from app.routes.categories import categories_bp
    from app.routes.tags import tags_bp
    from app.routes.users import users_bp
    
    app.register_blueprint(auth_bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(posts_bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(categories_bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(tags_bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(users_bp, url_prefix=app.config['API_PREFIX'])
    
    # Setup error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return {"error": "Internal server error"}, 500
    
    return app
