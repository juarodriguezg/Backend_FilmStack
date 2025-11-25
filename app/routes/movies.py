from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.schemas import MovieCreateSchema, MovieResponseSchema
from app.services import MovieService, TMDbService

movies_bp = Blueprint('movies', __name__)

movie_create_schema = MovieCreateSchema()
movie_response_schema = MovieResponseSchema()
movies_response_schema = MovieResponseSchema(many=True)


@movies_bp.route('/search', methods=['GET'])
def search_movies():
    """Endpoint para buscar películas en TheMovieDB (TMDB)"""
    try:
        title = request.args.get('title')
        
        if not title or len(title) < 1:
            return jsonify({
                'success': False,
                'error': 'El título es requerido'
            }), 400
        
        results = TMDbService.search_movies(title)
        
        return jsonify({
            'success': True,
            'results': results
        }), 200
    
    except Exception as err:
        return jsonify({
            'success': False,
            'error': 'Error al buscar películas'
        }), 500


@movies_bp.route('/', methods=['POST'])
@jwt_required()
def create_movie():
    """Endpoint para crear nueva película"""
    try:
        user_id = get_jwt_identity()
        data = movie_create_schema.load(request.get_json())
        
        movie = MovieService.create_movie(
            user_id=user_id,
            title=data['title'],
            year=data['year'],
            director=data['director'],
            genre=data['genre'],
            tmdb_id=data.get('tmdb_id')
        )
        
        return jsonify({
            'success': True,
            'message': 'Película creada exitosamente',
            'data': movie_response_schema.dump(movie)
        }), 201
    
    except ValidationError as err:
        return jsonify({
            'success': False,
            'error': 'Validación fallida',
            'details': err.messages
        }), 400
    except Exception as err:
        return jsonify({
            'success': False,
            'error': 'Error al crear película'
        }), 500


@movies_bp.route('/', methods=['GET'])
@jwt_required()
def get_movies():
    """Endpoint para obtener películas del usuario"""
    try:
        user_id = get_jwt_identity()
        movies = MovieService.get_user_movies(user_id)
        
        return jsonify({
            'success': True,
            'data': {
                'movies': movies_response_schema.dump(movies),
                'total': len(movies)
            }
        }), 200
    
    except Exception as err:
        return jsonify({
            'success': False,
            'error': 'Error al obtener películas'
        }), 500


@movies_bp.route('/<int:movie_id>', methods=['GET'])
@jwt_required()
def get_movie(movie_id):
    """Endpoint para obtener película específica"""
    try:
        user_id = get_jwt_identity()
        movie = MovieService.get_movie_by_id(movie_id, user_id)
        
        if not movie:
            return jsonify({
                'success': False,
                'error': 'Película no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'data': movie_response_schema.dump(movie)
        }), 200
    
    except Exception as err:
        return jsonify({
            'success': False,
            'error': 'Error al obtener película'
        }), 500


@movies_bp.route('/<int:movie_id>', methods=['PUT'])
@jwt_required()
def update_movie(movie_id):
    """Endpoint para actualizar película"""
    try:
        user_id = get_jwt_identity()
        data = movie_create_schema.load(request.get_json(), partial=True)
        
        movie = MovieService.update_movie(movie_id, user_id, **data)
        
        if not movie:
            return jsonify({
                'success': False,
                'error': 'Película no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Película actualizada exitosamente',
            'data': movie_response_schema.dump(movie)
        }), 200
    
    except ValidationError as err:
        return jsonify({
            'success': False,
            'error': 'Validación fallida',
            'details': err.messages
        }), 400
    except Exception as err:
        return jsonify({
            'success': False,
            'error': 'Error al actualizar película'
        }), 500


@movies_bp.route('/<int:movie_id>', methods=['DELETE'])
@jwt_required()
def delete_movie(movie_id):
    """Endpoint para eliminar película"""
    try:
        user_id = get_jwt_identity()
        success = MovieService.delete_movie(movie_id, user_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Película no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Película eliminada exitosamente'
        }), 200
    
    except Exception as err:
        return jsonify({
            'success': False,
            'error': 'Error al eliminar película'
        }), 500