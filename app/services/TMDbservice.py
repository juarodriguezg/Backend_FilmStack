import requests
from app import db
from app.models import User, Movie
from flask import current_app
from sqlalchemy.exc import IntegrityError

class TMDbService:
    """Servicio para consumir API de TheMovieDB (TMDB)"""
    
    TMDB_BASE_URL = 'https://api.themoviedb.org/3'
    TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'
    
    @staticmethod
    def search_movies(title):
        """Buscar películas por título"""
        try:
            api_key = current_app.config.get('TMDB_API_KEY')
            
            if not api_key:
                return []
            
            params = {
                'api_key': api_key,
                'query': title,
                'include_adult': False
            }
            
            response = requests.get(
                f'{TMDbService.TMDB_BASE_URL}/search/movie',
                params=params,
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Formatear resultados para facilitar uso en frontend
            results = []
            for movie in data.get('results', []):
                results.append({
                    'id': movie.get('id'),
                    'title': movie.get('title'),
                    'poster_path': movie.get('poster_path'),
                    'release_date': movie.get('release_date'),
                    'overview': movie.get('overview'),
                    'vote_average': movie.get('vote_average')
                })
            
            return results
        
        except requests.exceptions.RequestException:
            return []
    
    @staticmethod
    def get_movie_details(movie_id):
        """Obtener detalles completos de película por TMDB ID"""
        try:
            api_key = current_app.config.get('TMDB_API_KEY')
            
            if not api_key:
                return None
            
            params = {
                'api_key': api_key
            }
            
            response = requests.get(
                f'{TMDbService.TMDB_BASE_URL}/movie/{movie_id}',
                params=params,
                timeout=5
            )
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.RequestException:
            return None
    
    @staticmethod
    def get_poster_url(movie_id):
        """Obtener URL del poster de una película"""
        details = TMDbService.get_movie_details(movie_id)
        
        if details and details.get('poster_path'):
            return f"{TMDbService.TMDB_IMAGE_BASE_URL}{details.get('poster_path')}"
        
        return None