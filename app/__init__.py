from flask import Flask
from flask_socketio import SocketIO

# Initialize extensions here but don't configure them until create_app
socketio = SocketIO()

def create_app(config_name="default"):
    """Application factory pattern."""
    app = Flask(__name__, static_url_path='/static')
    
    # Import and apply configuration
    from app.config import config_dict
    app.config.from_object(config_dict[config_name])
    config_dict[config_name].init_app(app)
    
    # Initialize extensions with app
    from app.extensions import db, migrate, csrf, limiter, cors
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)
    cors.init_app(app)
    
    # Initialize SocketIO with app (gevent/eventlet worker in production)
    socketio.init_app(app, 
                     cors_allowed_origins=app.config.get('CORS_ORIGINS', '*'),
                     async_mode=app.config.get('SOCKETIO_ASYNC_MODE', None),
                     message_queue=app.config.get('SOCKETIO_MESSAGE_QUEUE', None))
    
    # Register blueprints
    from app.blueprints import register_blueprints
    register_blueprints(app)
    
    # Register auth module
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    """Register error handlers for common HTTP errors."""
    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        return render_template('errors/500.html'), 500
