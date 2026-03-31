"""
Grade Analysis Flask Application Factory

This module provides the create_app factory function for the Flask application.

MIT License
Copyright (c) 2026 Grade Analysis App
"""

from flask import Flask
from typing import Optional, Dict, Any
import os
import sys

from app.config import Config, DevelopmentConfig, ProductionConfig, get_base_path
from app.extensions import init_extensions
from app.routes import register_blueprints
from app.core.data_service import SessionDataService


def create_app(config: Optional[Config] = None) -> Flask:
    """Create and configure the Flask application.
    
    Args:
        config: Optional configuration class. If None, uses environment-based config.
        
    Returns:
        Configured Flask application instance.
    """
    # Get base path for PyInstaller compatibility
    base_path = get_base_path()
    
    # For PyInstaller, templates and static are bundled and accessible via sys._MEIPASS
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        template_folder = os.path.join(sys._MEIPASS, 'templates')
        static_folder = os.path.join(sys._MEIPASS, 'static')
    else:
        # Running as script
        template_folder = os.path.join(base_path, 'templates')
        static_folder = os.path.join(base_path, 'static')
    
    app = Flask(__name__, 
                template_folder=template_folder,
                static_folder=static_folder)
    
    # Load configuration
    if config is None:
        config = _get_config_from_env()
    
    app.config.from_object(config)
    
    # Initialize config (sets UPLOAD_FOLDER dynamically)
    config.init_app(app)
    
    # Initialize extensions
    init_extensions(app)
    
    # Initialize session-bound data service
    app.session_data_service = SessionDataService(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Exempt API blueprint from CSRF protection
    if hasattr(app, 'csrf'):
        from app.routes.api import api_bp
        app.csrf.exempt(api_bp)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Register context processors
    _register_context_processors(app)
    
    return app


def _get_config_from_env() -> Config:
    """Get configuration class based on FLASK_ENV environment variable.
    
    Returns:
        Appropriate Config subclass.
    """
    env = os.environ.get('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig()
    else:
        return DevelopmentConfig()


def _register_error_handlers(app: Flask) -> None:
    """Register global error handlers.
    
    Args:
        app: Flask application instance.
    """
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        app.logger.error(f'Server Error: {error}')
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(413)
    def too_large_error(error):
        from flask import flash, redirect, url_for
        flash('文件太大，请上传小于16MB的文件', 'error')
        return redirect(url_for('main.index'))


def _register_context_processors(app: Flask) -> None:
    """Register Jinja2 context processors.
    
    Args:
        app: Flask application instance.
    """
    @app.context_processor
    def inject_conf_vars():
        """Inject configuration variables into all templates."""
        return {
            'app_name': '高中成绩分析系统',
            'app_version': '3.0.0'
        }
