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

# Tests de Autenticación

class TestAuth:
    """Tests para endpoints de autenticación"""
    
    def test_register_success(self, client):
        """Test registro exitoso"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] == True
        assert data['data']['username'] == 'newuser'
    
    def test_register_missing_fields(self, client):
        """Test registro con campos faltantes"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False
    
    def test_register_duplicate_email(self, client):
        """Test registro con email duplicado"""
        # Primer registro
        client.post('/api/auth/register', json={
            'username': 'user1',
            'email': 'duplicate@example.com',
            'password': 'password123'
        })
        
        # Segundo registro con mismo email
        response = client.post('/api/auth/register', json={
            'username': 'user2',
            'email': 'duplicate@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 400
    
    def test_login_success(self, client):
        """Test login exitoso"""
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
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'access_token' in data['data']
    
    def test_login_invalid_credentials(self, client):
        """Test login con credenciales inválidas"""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] == False
    
    def test_get_current_user(self, client, auth_headers):
        """Test obtener usuario actual"""
        response = client.get('/api/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['data']['username'] == 'testuser'
    
    def test_get_current_user_no_token(self, client):
        """Test obtener usuario sin token"""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
