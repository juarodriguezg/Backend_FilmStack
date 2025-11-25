from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Movie(db.Model):
    """Modelo de Película"""
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    director = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(255), nullable=False)
    poster_url = db.Column(db.String(500))
    imdb_id = db.Column(db.String(20), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convertir película a diccionario"""
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'director': self.director,
            'genre': self.genre,
            'poster_url': self.poster_url,
            'imdb_id': self.imdb_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }