"""
Application Configuration Classes

This module defines configuration classes for different environments.
"""

import os
import sys
from typing import Dict, Any


def get_base_path() -> str:
    """Get the base path for the application.
    
    When running as a PyInstaller bundle, use the executable's directory.
    When running as a script, use the project root directory.
    
    Returns:
        Base path string.
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return os.path.dirname(sys.executable)
    else:
        # Running as script - go up one level from app/ to project root
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    """Base configuration class.
    
    Common settings for all environments.
    """
    
    # Flask core
    SECRET_KEY = os.environ.get('SECRET_KEY', 'grade-analysis-secret-key-change-in-production')
    
    # File upload settings - will be set dynamically in init_app
    UPLOAD_FOLDER = None  # Will be set at runtime
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
    
    # Session settings
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Data settings
    DATA_EXPIRY_HOURS = 24  # How long to keep session data
    
    # Logging
    LOG_LEVEL = 'INFO'
    
    @staticmethod
    def init_app(app) -> None:
        """Initialize application with this configuration.
        
        Args:
            app: Flask application instance.
        """
        # Set UPLOAD_FOLDER dynamically at runtime for PyInstaller compatibility
        # This ensures the path is computed when the app actually starts
        upload_folder = os.path.join(get_base_path(), 'data')
        app.config['UPLOAD_FOLDER'] = upload_folder
        
        # Create upload folder if not exists
        os.makedirs(upload_folder, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    TESTING = False
    
    # Override secret key from environment
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-must-change-this-in-production'


class TestingConfig(Config):
    """Testing configuration."""
    
    DEBUG = True
    TESTING = True
    LOG_LEVEL = 'DEBUG'
    
    # Use in-memory storage for tests
    UPLOAD_FOLDER = '/tmp/test_uploads'


# Configuration dictionary for easy access
config_by_name: Dict[str, Config] = {
    'development': DevelopmentConfig(),
    'production': ProductionConfig(),
    'testing': TestingConfig(),
    'default': DevelopmentConfig()
}
