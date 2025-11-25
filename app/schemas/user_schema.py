from marshmallow import Schema, fields, validate, ValidationError

class UserRegisterSchema(Schema):
    """Schema para registro de usuario"""
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=80),
        error_messages={'required': 'El nombre de usuario es requerido'}
    )
    email = fields.Email(
        required=True,
        error_messages={'required': 'El email es requerido', 'invalid': 'Email inválido'}
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6),
        error_messages={'required': 'La contraseña es requerida', 
                       'validator_failed': 'La contraseña debe tener al menos 6 caracteres'}
    )

class UserLoginSchema(Schema):
    """Schema para login de usuario"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserResponseSchema(Schema):
    """Schema para respuesta de usuario"""
    id = fields.Int()
    username = fields.Str()
    email = fields.Email()
    created_at = fields.Str()

