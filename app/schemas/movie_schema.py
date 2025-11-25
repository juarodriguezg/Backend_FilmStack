from marshmallow import Schema, fields, validate, ValidationError

class MovieCreateSchema(Schema):
    """Schema para crear/actualizar película"""
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
        error_messages={'required': 'El título es requerido'}
    )
    year = fields.Int(
        required=True,
        validate=validate.Range(min=1800, max=2100),
        error_messages={'required': 'El año es requerido'}
    )
    director = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
        error_messages={'required': 'El director es requerido'}
    )
    genre = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
        error_messages={'required': 'El género es requerido'}
    )
    tmdb_id = fields.Str(allow_none=True)

class MovieResponseSchema(Schema):
    """Schema para respuesta de película"""
    id = fields.Int()
    title = fields.Str()
    year = fields.Int()
    director = fields.Str()
    genre = fields.Str()
    poster_url = fields.Str()
    imdb_id = fields.Str()
    user_id = fields.Int()
    created_at = fields.Str()
    updated_at = fields.Str()