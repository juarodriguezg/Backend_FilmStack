import os
from app import create_app, db
from app.models import User, Movie

# Crear aplicación
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

@app.shell_context_processor
def make_shell_context():
    """Contexto para flask shell"""
    return {'db': db, 'User': User, 'Movie': Movie}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )