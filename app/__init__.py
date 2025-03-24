from flask import Flask
from app.routes import home  # Import your route function here

def create_app():
    app = Flask(__name__)

    # Register routes
    app.add_url_rule('/', 'home', home)  # This connects the home function to the root URL

    return app
