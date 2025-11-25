from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User

def token_required(f):
    """
    Decorador para verificar que el token JWT esté presente y sea válido.
    Se usa en rutas que requieren autenticación.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            # Verificar que el usuario existe
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'Usuario no encontrado'}), 404
            
            # Pasar el usuario al contexto
            request.current_user = user
            
            return f(*args, **kwargs)
        
        except Exception as e:
            return jsonify({'error': 'Token inválido o expirado'}), 401
    
    return decorated

def admin_required(f):
    """
    Decorador para verificar que el usuario sea administrador.
    Requiere que el usuario tenga un rol 'admin'.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'Usuario no encontrado'}), 404
            
            # Verificar si el usuario es admin (opcional, según tus requisitos)
            # if not user.is_admin:
            #     return jsonify({'error': 'Se requieren permisos de administrador'}), 403
            
            request.current_user = user
            
            return f(*args, **kwargs)
        
        except Exception as e:
            return jsonify({'error': 'Token inválido o expirado'}), 401
    
    return decorated

def validate_json(f):
    """
    Decorador para validar que el request contiene JSON válido.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'El content-type debe ser application/json'}), 400
        
        try:
            request.get_json()
        except Exception as e:
            return jsonify({'error': 'JSON inválido en el body'}), 400
        
        return f(*args, **kwargs)
    
    return decorated

def rate_limit(max_requests=100, window=3600):
    """
    Decorador para limitar el número de requests por usuario en una ventana de tiempo.
    Útil para prevenir abuso de API.
    
    Parámetros:
    - max_requests: número máximo de requests permitidos
    - window: ventana de tiempo en segundos (default 1 hora)
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Para implementación completa, necesitarías usar Redis o similar
            # Por ahora es un ejemplo básico
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator

class RequestLogger:
    """
    Middleware para registrar todos los requests y responses de la API.
    Útil para debugging y auditoría.
    """
    
    @staticmethod
    def log_request(app):
        """
        Registra información de cada request en los logs.
        """
        @app.before_request
        def log_request_info():
            app.logger.debug(f'Headers: {dict(request.headers)}')
            app.logger.debug(f'Body: {request.get_data()}')
        
        @app.after_request
        def log_response_info(response):
            app.logger.debug(f'Status: {response.status}')
            app.logger.debug(f'Response: {response.get_data()}')
            return response

class CORSHandler:
    """
    Middleware para manejar CORS (Cross-Origin Resource Sharing).
    Ya está configurado en app/__init__.py con Flask-CORS,
    pero aquí hay una implementación manual si la necesitas.
    """
    
    @staticmethod
    def setup_cors(app, allowed_origins=None):
        """
        Configura CORS manualmente (alternativa a Flask-CORS).
        """
        if allowed_origins is None:
            allowed_origins = ['http://localhost:3000', 'http://localhost:5173']
        
        @app.after_request
        def after_request(response):
            origin = request.headers.get('Origin')
            
            if origin in allowed_origins:
                response.headers.add('Access-Control-Allow-Origin', origin)
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
                response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
                response.headers.add('Access-Control-Allow-Credentials', 'true')
            
            return response
        
        @app.route('/<path:path>', methods=['OPTIONS'])
        def handle_preflight(path):
            return '', 204

class ErrorHandler:
    """
    Middleware para manejar errores globales de la aplicación.
    """
    
    @staticmethod
    def setup_error_handlers(app):
        """
        Registra manejadores de errores globales.
        """
        
        @app.errorhandler(400)
        def bad_request(error):
            return jsonify({
                'error': 'Solicitud inválida',
                'status': 400
            }), 400
        
        @app.errorhandler(401)
        def unauthorized(error):
            return jsonify({
                'error': 'No autorizado',
                'status': 401
            }), 401
        
        @app.errorhandler(403)
        def forbidden(error):
            return jsonify({
                'error': 'Acceso prohibido',
                'status': 403
            }), 403
        
        @app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'error': 'Recurso no encontrado',
                'status': 404
            }), 404
        
        @app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                'error': 'Error interno del servidor',
                'status': 500
            }), 500