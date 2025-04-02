from flask import Blueprint
from flask_login import LoginManager
from app.extensions import login_manager
from app.models import User

# Initialize blueprint
bp = Blueprint('auth', __name__)  # Let it use default templates/auth/ location

# Import routes AFTER blueprint creation to avoid circular imports
from app.auth import routes

# Login manager configuration
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'