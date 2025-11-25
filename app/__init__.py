# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_name='development'):
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'].split(','))
    
    # Registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.movies import movies_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(movies_bp, url_prefix='/api/movies')
    
    # Crear tablas
    with app.app_context():
        db.create_all()
    
    return app

# app/models/__init__.py
from app.models.user import User
from app.models.movie import Movie

__all__ = ['User', 'Movie']

# app/routes/__init__.py
from app.routes.auth import auth_bp
from app.routes.movies import movies_bp

__all__ = ['auth_bp', 'movies_bp']

# app/schemas/__init__.py
from app.schemas.user_schema import (
    UserRegisterSchema,
    UserLoginSchema,
    UserResponseSchema
)
from app.schemas.movie_schema import (
    MovieCreateSchema,
    MovieResponseSchema
)

__all__ = [
    'UserRegisterSchema',
    'UserLoginSchema',
    'UserResponseSchema',
    'MovieCreateSchema',
    'MovieResponseSchema'
]

# app/services/__init__.py
from app.services.auth_service import AuthService
from app.services.movie_service import MovieService
from app.services.tmdb_service import TMDbService

__all__ = ['AuthService', 'MovieService', 'TMDbService']

# app/utils/__init__.py
from app.utils.utils import (
    Response,
    Pagination,
    handle_errors,
    validate_request_data,
    require_auth,
    ensure_json_content_type
)

__all__ = [
    'Response',
    'Pagination',
    'handle_errors',
    'validate_request_data',
    'require_auth',
    'ensure_json_content_type'
]