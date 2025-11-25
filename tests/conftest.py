import pytest
import os
from app import create_app, db
from app.models import User, Movie


@pytest.fixture
def app():
    """Crear app para testing con BD en memoria"""
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente HTTP para hacer requests a la app"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner para comandos Flask"""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """
    Headers con token JWT válido para autenticación.
    Registra y login automáticamente un usuario de prueba.
    """
    # Registrar usuario de prueba
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    # Hacer login
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    token = response.get_json()['data']['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def test_user(client):
    """
    Crea un usuario de prueba y retorna sus datos.
    Incluye el token JWT.
    """
    # Registrar
    client.post('/api/auth/register', json={
        'username': 'testuser2',
        'email': 'testuser2@example.com',
        'password': 'password123'
    })
    
    # Login
    response = client.post('/api/auth/login', json={
        'email': 'testuser2@example.com',
        'password': 'password123'
    })
    
    data = response.get_json()['data']
    
    return {
        'user': data['user'],
        'token': data['access_token'],
        'headers': {'Authorization': f"Bearer {data['access_token']}"}
    }


@pytest.fixture
def test_movie(client, auth_headers):
    """
    Crea una película de prueba para el usuario autenticado.
    """
    response = client.post('/api/movies',
        headers=auth_headers,
        json={
            'title': 'Test Movie',
            'year': 2023,
            'director': 'Test Director',
            'genre': 'Test Genre'
        }
    )
    
    return response.get_json()['data']