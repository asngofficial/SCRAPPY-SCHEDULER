from flask import Flask
from config import Config
from .extensions import db, login_manager, mail, migrate  # Added migrate here

def create_app(config_class=Config):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Initialize extensions - all at same indentation level
    db.init_app(app)
    migrate.init_app(app, db)  # Fixed indentation
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Import models AFTER db is initialized
    from .models import User
    
    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.home.routes import bp as home_bp
    from app.auth.routes import bp as auth_bp
    
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app