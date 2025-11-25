from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.schemas import UserRegisterSchema, UserLoginSchema, UserResponseSchema
from app.services import AuthService
from app.models import User

auth_bp = Blueprint('auth', __name__)

register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()
user_response_schema = UserResponseSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    """Endpoint para registrar nuevo usuario"""
    try:
        # Validar datos
        data = register_schema.load(request.get_json())
        
        # Crear usuario
        user = AuthService.register_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'user': user_response_schema.dump(user)
        }), 201
    
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except ValueError as err:
        return jsonify({'error': str(err)}), 400
    except Exception as err:
        return jsonify({'error': 'Error al registrar usuario'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para iniciar sesión"""
    try:
        # Validar datos
        data = login_schema.load(request.get_json())
        
        # Autenticar usuario
        user = AuthService.authenticate_user(
            email=data['email'],
            password=data['password']
        )
        
        if not user:
            return jsonify({'error': 'Email o contraseña incorrectos'}), 401
        
        # Crear token JWT
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Inicio de sesión exitoso',
            'access_token': access_token,
            'user': user_response_schema.dump(user)
        }), 200
    
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except Exception as err:
        return jsonify({'error': 'Error al iniciar sesión'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Endpoint para obtener usuario actual"""
    try:
        user_id = get_jwt_identity()
        user = AuthService.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify(user_response_schema.dump(user)), 200
    
    except Exception as err:
        return jsonify({'error': 'Error al obtener usuario'}), 500