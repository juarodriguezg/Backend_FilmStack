from app import db
from app.models.user import User


class AuthService:
    """Servicio de autenticación"""
    
    @staticmethod
    def register_user(username, email, password):
        """Registrar nuevo usuario"""
        # Verificar si usuario ya existe
        if User.query.filter_by(username=username).first():
            raise ValueError('El nombre de usuario ya existe')
        
        if User.query.filter_by(email=email).first():
            raise ValueError('El email ya está registrado')
        
        # Crear usuario
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def authenticate_user(email, password):
        """Autenticar usuario"""
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return None
        
        return user
    
    @staticmethod
    def get_user_by_id(user_id):
        """Obtener usuario por ID"""
        return User.query.get(user_id)