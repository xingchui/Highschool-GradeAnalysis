"""
Application Configuration Classes

This module defines configuration classes for different environments.
"""

import os
from typing import Dict, Any


class Config:
    """Base configuration class.
    
    Common settings for all environments.
    """
    
    # Flask core
    SECRET_KEY = os.environ.get('SECRET_KEY', 'grade-analysis-secret-key-change-in-production')
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
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
        # Create upload folder if not exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


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
