import os
from dotenv import load_dotenv
SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/project.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

load_dotenv()

class Config:
    # App Configuration
    SECRET_KEY = os.getenv('SECRET_KEY')  # No fallback in production!
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///project.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ('true', '1', 't')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'samuelafon1@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'samuelafon1@gmail.com')
    ADMINS = ['samuelafon1@gmail.com']  # For error notifications
    
    # ClickSend Configuration
    CLICKSEND_USERNAME = os.getenv('CLICKSEND_USERNAME')
    CLICKSEND_PASSWORD = os.getenv('CLICKSEND_PASSWORD')