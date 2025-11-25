from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity


def handle_errors(f):
    """
    Decorador para envolver funciones y manejar excepciones comunes.
    Retorna errores en formato JSON consistente.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except KeyError as e:
            return jsonify({'error': f'Falta el campo: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    return decorated


def validate_request_data(*required_fields):
    """
    Decorador para validar que los campos requeridos estén presentes en el request.
    
    Uso:
    @validate_request_data('username', 'email', 'password')
    def register():
        ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type debe ser application/json'}), 400
            
            data = request.get_json()
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({
                    'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}'
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator


def require_auth(f):
    """
    Decorador simplificado para requerir autenticación JWT.
    Similar a @jwt_required() pero con manejo de errores personalizado.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            request.user_id = user_id
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Autenticación requerida. Proporciona un token JWT válido'}), 401
    
    return decorated


def ensure_json_content_type(f):
    """
    Decorador para asegurar que el request tiene Content-Type: application/json
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            if not request.is_json:
                return jsonify({'error': 'Content-Type debe ser application/json'}), 400
        
        return f(*args, **kwargs)
    
    return decorated


class Response:
    """
    Clase de utilidad para crear respuestas JSON consistentes.
    """
    
    @staticmethod
    def success(data=None, message='Éxito', status_code=200):
        """Respuesta exitosa"""
        response = {
            'success': True,
            'message': message
        }
        if data is not None:
            response['data'] = data
        
        return jsonify(response), status_code
    
    @staticmethod
    def error(message='Error', status_code=400, details=None):
        """Respuesta de error"""
        response = {
            'success': False,
            'error': message
        }
        if details is not None:
            response['details'] = details
        
        return jsonify(response), status_code
    
    @staticmethod
    def created(data, message='Recurso creado exitosamente'):
        """Respuesta de recurso creado (201)"""
        return Response.success(data=data, message=message, status_code=201)
    
    @staticmethod
    def not_found(message='Recurso no encontrado'):
        """Respuesta de recurso no encontrado (404)"""
        return Response.error(message=message, status_code=404)
    
    @staticmethod
    def unauthorized(message='No autorizado'):
        """Respuesta no autorizada (401)"""
        return Response.error(message=message, status_code=401)
    
    @staticmethod
    def forbidden(message='Acceso prohibido'):
        """Respuesta acceso prohibido (403)"""
        return Response.error(message=message, status_code=403)
    
    @staticmethod
    def bad_request(message='Solicitud inválida', details=None):
        """Respuesta solicitud inválida (400)"""
        return Response.error(message=message, status_code=400, details=details)


class Pagination:
    """
    Clase de utilidad para manejar paginación en listados.
    """
    
    @staticmethod
    def paginate(query, page=1, per_page=10):
        """
        Pagina una query de SQLAlchemy.
        
        Retorna diccionario con:
        - items: lista de items
        - total: total de items
        - page: página actual
        - pages: total de páginas
        - has_next: si hay siguiente página
        - has_prev: si hay página anterior
        """
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': paginated.items,
            'total': paginated.total,
            'page': page,
            'pages': paginated.pages,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        }
    
    @staticmethod
    def get_pagination_params(request, default_page=1, default_per_page=10):
        """
        Extrae parámetros de paginación del request.
        """
        try:
            page = int(request.args.get('page', default_page))
            per_page = int(request.args.get('per_page', default_per_page))
            
            # Validar ranges
            page = max(1, page)
            per_page = max(1, min(100, per_page))  # Máximo 100 items por página
            
            return page, per_page
        except (ValueError, TypeError):
            return default_page, default_per_page