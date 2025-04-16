import os
from dotenv import load_dotenv
SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/project.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')  # No fallback in production!
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///project.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CLICKSEND_USERNAME = os.getenv('CLICKSEND_USERNAME')  # No hardcoded values
    CLICKSEND_PASSWORD = os.getenv('CLICKSEND_PASSWORD')  # No hardcoded values

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'samuelafon1@gmail.com'
MAIL_PASSWORD = 'Luslus2003*'
MAIL_DEFAULT_SENDER = 'samuelafon1@gmail.com'