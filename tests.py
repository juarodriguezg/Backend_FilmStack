import pytest
from app import create_app, db
from app.models import User, Movie


@pytest.fixture
def app():
    """Crear app en modo testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de prueba"""
    return app.test_client()


@pytest.fixture
def user_data():
    """Datos de usuario para testing"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }


@pytest.fixture
def registered_user(client, user_data):
    """Registrar usuario y retornar sus datos"""
    client.post('/api/auth/register', json=user_data)
    return user_data


@pytest.fixture
def auth_token(client, registered_user):
    """Obtener token de autenticación"""
    response = client.post('/api/auth/login', json={
        'email': registered_user['email'],
        'password': registered_user['password']
    })
    return response.get_json()['data']['access_token']


# ============= TESTS DE AUTENTICACIÓN =============

class TestAuth:
    """Tests para endpoints de autenticación"""
    
    def test_register_success(self, client, user_data):
        """Registrar usuario exitosamente"""
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 201
        assert response.get_json()['success'] is True
        assert response.get_json()['data']['username'] == user_data['username']
    
    def test_register_duplicate_username(self, client, registered_user):
        """No permitir registro con username duplicado"""
        response = client.post('/api/auth/register', json={
            'username': registered_user['username'],
            'email': 'another@example.com',
            'password': 'password123'
        })
        assert response.status_code == 400
        assert response.get_json()['success'] is False
    
    def test_register_duplicate_email(self, client, registered_user):
        """No permitir registro con email duplicado"""
        response = client.post('/api/auth/register', json={
            'username': 'otherusername',
            'email': registered_user['email'],
            'password': 'password123'
        })
        assert response.status_code == 400
        assert response.get_json()['success'] is False
    
    def test_register_missing_fields(self, client):
        """Validar que se requieren todos los campos"""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com'
            # Falta password
        })
        assert response.status_code == 400
    
    def test_login_success(self, client, registered_user):
        """Login exitoso"""
        response = client.post('/api/auth/login', json={
            'email': registered_user['email'],
            'password': registered_user['password']
        })
        assert response.status_code == 200
        assert response.get_json()['success'] is True
        assert 'access_token' in response.get_json()['data']
    
    def test_login_invalid_password(self, client, registered_user):
        """Login con contraseña incorrecta"""
        response = client.post('/api/auth/login', json={
            'email': registered_user['email'],
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
        assert response.get_json()['success'] is False
    
    def test_login_nonexistent_user(self, client):
        """Login con email que no existe"""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        })
        assert response.status_code == 401
    
    def test_get_current_user(self, client, auth_token):
        """Obtener datos del usuario actual"""
        response = client.get(
            '/api/auth/me',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response.status_code == 200
        assert response.get_json()['success'] is True
        assert response.get_json()['data']['username'] == 'testuser'
    
    def test_get_current_user_without_token(self, client):
        """No permitir acceso sin token"""
        response = client.get('/api/auth/me')
        assert response.status_code == 401


# ============= TESTS DE PELÍCULAS =============

class TestMovies:
    """Tests para endpoints de películas"""
    
    def test_search_movies(self, client):
        """Buscar películas en TMDB"""
        response = client.get('/api/movies/search?title=Inception')
        assert response.status_code == 200
        assert response.get_json()['success'] is True
        assert 'results' in response.get_json()
    
    def test_search_movies_empty_title(self, client):
        """Validar búsqueda sin título"""
        response = client.get('/api/movies/search?title=')
        assert response.status_code == 400
    
    def test_create_movie_success(self, client, auth_token):
        """Crear película exitosamente"""
        movie_data = {
            'title': 'Test Movie',
            'year': 2023,
            'director': 'Test Director',
            'genre': 'Action'
        }
        response = client.post(
            '/api/movies/',
            json=movie_data,
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response.status_code == 201
        assert response.get_json()['success'] is True
        assert response.get_json()['data']['title'] == 'Test Movie'
    
    def test_create_movie_without_token(self, client):
        """No permitir crear película sin autenticación"""
        response = client.post('/api/movies/', json={
            'title': 'Test Movie',
            'year': 2023,
            'director': 'Test Director',
            'genre': 'Action'
        })
        assert response.status_code == 401
    
    def test_create_movie_invalid_year(self, client, auth_token):
        """Validar año de película"""
        response = client.post(
            '/api/movies/',
            json={
                'title': 'Test Movie',
                'year': 1700,  # Menor que 1800
                'director': 'Test Director',
                'genre': 'Action'
            },
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response.status_code == 400
    
    def test_get_user_movies(self, client, auth_token):
        """Obtener películas del usuario"""
        # Crear película primero
        client.post(
            '/api/movies/',
            json={
                'title': 'Movie 1',
                'year': 2023,
                'director': 'Director 1',
                'genre': 'Action'
            },
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        response = client.get(
            '/api/movies/',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response.status_code == 200
        assert response.get_json()['success'] is True
        assert response.get_json()['data']['total'] == 1
    
    def test_get_movie_by_id(self, client, auth_token):
        """Obtener película específica"""
        # Crear película
        create_response = client.post(
            '/api/movies/',
            json={
                'title': 'Test Movie',
                'year': 2023,
                'director': 'Test Director',
                'genre': 'Action'
            },
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        movie_id = create_response.get_json()['data']['id']
        
        # Obtener película
        response = client.get(
            f'/api/movies/{movie_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response.status_code == 200
        assert response.get_json()['data']['title'] == 'Test Movie'
    
    def test_get_nonexistent_movie(self, client, auth_token):
        """Obtener película que no existe"""
        response = client.get(
            '/api/movies/99999',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response.status_code == 404
    
    def test_update_movie(self, client, auth_token):
        """Actualizar película"""
        # Crear película
        create_response = client.post(
            '/api/movies/',
            json={
                'title': 'Original Title',
                'year': 2023,
                'director': 'Original Director',
                'genre': 'Action'
            },
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        movie_id = create_response.get_json()['data']['id']
        
        # Actualizar película
        response = client.put(
            f'/api/movies/{movie_id}',
            json={'title': 'Updated Title'},
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response.status_code == 200
        assert response.get_json()['data']['title'] == 'Updated Title'
    
    def test_delete_movie(self, client, auth_token):
        """Eliminar película"""
        # Crear película
        create_response = client.post(
            '/api/movies/',
            json={
                'title': 'To Delete',
                'year': 2023,
                'director': 'Test Director',
                'genre': 'Action'
            },
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        movie_id = create_response.get_json()['data']['id']
        
        # Eliminar película
        response = client.delete(
            f'/api/movies/{movie_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response.status_code == 200
        assert response.get_json()['success'] is True
        
        # Verificar que está eliminada
        get_response = client.get(
            f'/api/movies/{movie_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert get_response.status_code == 404