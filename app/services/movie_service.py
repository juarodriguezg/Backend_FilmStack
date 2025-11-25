import requests
import TMDbservice
from app import db
from app.models import User, Movie
from flask import current_app
from sqlalchemy.exc import IntegrityError

class MovieService:
    """Servicio de películas"""
    
    @staticmethod
    def create_movie(user_id, title, year, director, genre, tmdb_id=None):
        """Crear nueva película"""
        movie = Movie(
            title=title,
            year=year,
            director=director,
            genre=genre,
            imdb_id=tmdb_id,  # Reutilizamos el campo para TMDB ID
            user_id=user_id
        )
        
        # Si existe tmdb_id, obtener poster de TMDB
        if tmdb_id:
            poster_url = TMDbService.get_poster_url(tmdb_id)
            if poster_url:
                movie.poster_url = poster_url
        
        db.session.add(movie)
        db.session.commit()
        
        return movie
    
    @staticmethod
    def get_user_movies(user_id):
        """Obtener películas del usuario"""
        return Movie.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def get_movie_by_id(movie_id, user_id):
        """Obtener película específica del usuario"""
        return Movie.query.filter_by(id=movie_id, user_id=user_id).first()
    
    @staticmethod
    def update_movie(movie_id, user_id, **kwargs):
        """Actualizar película"""
        movie = MovieService.get_movie_by_id(movie_id, user_id)
        
        if not movie:
            return None
        
        for key, value in kwargs.items():
            if hasattr(movie, key) and value is not None:
                setattr(movie, key, value)
        
        # Si se actualiza tmdb_id, obtener nuevo poster
        if 'imdb_id' in kwargs and kwargs['imdb_id']:
            poster_url = TMDbService.get_poster_url(kwargs['imdb_id'])
            if poster_url:
                movie.poster_url = poster_url
        
        db.session.commit()
        
        return movie
    
    @staticmethod
    def delete_movie(movie_id, user_id):
        """Eliminar película"""
        movie = MovieService.get_movie_by_id(movie_id, user_id)
        
        if not movie:
            return False
        
        db.session.delete(movie)
        db.session.commit()
        
        return True

