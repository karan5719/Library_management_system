import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if running on Render
if os.environ.get('RENDER'):
    load_dotenv('.env.production')

class Config:
    # Secret key for session management and CSRF protection (must match .env)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-this-in-production')
    
    # Database configuration (matching Railway MySQL)
    DB_HOST = os.environ.get('DB_HOST', 'nozomi.proxy.rlwy.net')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'wUiUFYWLRpyFsdLuLhsbQqCzFHPmlIMw')
    DB_NAME = os.environ.get('DB_NAME', 'librarys_management_system')
    DB_PORT = int(os.environ.get('DB_PORT', 29951))
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour in seconds
    
    # Security configurations
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'dev-salt-change-this'
    
    # Upload configuration
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Email configuration (if needed)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    @staticmethod
    def get_db_config():
        """Returns database configuration as a dictionary"""
        return {
            'host': Config.DB_HOST,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME,
            'port': Config.DB_PORT,
            'autocommit': True
        }

# Development configuration
class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

# Testing configuration
class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    DB_NAME = 'test_library_db'

# Production configuration
class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
