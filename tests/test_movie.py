import pytest
import json
from app import create_app, db
from app.models import User, Movie

@pytest.fixture
def app():
    """Crear app para testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente para hacer requests"""
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Headers con token JWT para autenticación"""
    # Registrar usuario
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    # Login
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    token = response.get_json()['data']['access_token']
    return {'Authorization': f'Bearer {token}'}



# Tests de Películas

class TestMovies:
    """Tests para endpoints de películas"""
    
    def test_create_movie(self, client, auth_headers):
        """Test crear película"""
        response = client.post('/api/movies', 
            headers=auth_headers,
            json={
                'title': 'Inception',
                'year': 2010,
                'director': 'Christopher Nolan',
                'genre': 'Sci-Fi',
                'tmdb_id': '27205'
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] == True
        assert data['data']['title'] == 'Inception'
    
    def test_create_movie_without_auth(self, client):
        """Test crear película sin autenticación"""
        response = client.post('/api/movies', json={
            'title': 'Inception',
            'year': 2010,
            'director': 'Christopher Nolan',
            'genre': 'Sci-Fi'
        })
        
        assert response.status_code == 401
    
    def test_get_user_movies(self, client, auth_headers):
        """Test obtener películas del usuario"""
        # Crear película
        client.post('/api/movies',
            headers=auth_headers,
            json={
                'title': 'Inception',
                'year': 2010,
                'director': 'Christopher Nolan',
                'genre': 'Sci-Fi'
            }
        )
        
        # Obtener películas
        response = client.get('/api/movies', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['data']['total'] == 1
    
    def test_get_movie_by_id(self, client, auth_headers):
        """Test obtener película específica"""
        # Crear película
        create_response = client.post('/api/movies',
            headers=auth_headers,
            json={
                'title': 'Inception',
                'year': 2010,
                'director': 'Christopher Nolan',
                'genre': 'Sci-Fi'
            }
        )
        
        movie_id = create_response.get_json()['data']['id']
        
        # Obtener película
        response = client.get(f'/api/movies/{movie_id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['data']['title'] == 'Inception'
    
    def test_update_movie(self, client, auth_headers):
        """Test actualizar película"""
        # Crear película
        create_response = client.post('/api/movies',
            headers=auth_headers,
            json={
                'title': 'Inception',
                'year': 2010,
                'director': 'Christopher Nolan',
                'genre': 'Sci-Fi'
            }
        )
        
        movie_id = create_response.get_json()['data']['id']
        
        # Actualizar película
        response = client.put(f'/api/movies/{movie_id}',
            headers=auth_headers,
            json={'genre': 'Action'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['data']['genre'] == 'Action'
    
    def test_delete_movie(self, client, auth_headers):
        """Test eliminar película"""
        # Crear película
        create_response = client.post('/api/movies',
            headers=auth_headers,
            json={
                'title': 'Inception',
                'year': 2010,
                'director': 'Christopher Nolan',
                'genre': 'Sci-Fi'
            }
        )
        
        movie_id = create_response.get_json()['data']['id']
        
        # Eliminar película
        response = client.delete(f'/api/movies/{movie_id}', headers=auth_headers)
        
        assert response.status_code == 200
        
        # Verificar que fue eliminada
        get_response = client.get(f'/api/movies/{movie_id}', headers=auth_headers)
        assert get_response.status_code == 404
    
    def test_search_movies(self, client):
        """Test buscar películas (sin autenticación)"""
        response = client.get('/api/movies/search?title=Inception')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'results' in data