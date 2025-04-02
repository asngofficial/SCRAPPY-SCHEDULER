from flask import Blueprint

bp = Blueprint('home', __name__)

from app.home import routes  # Import after creating bp to avoid circular imports