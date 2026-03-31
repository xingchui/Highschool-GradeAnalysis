"""
Flask Extensions Initialization

This module initializes Flask extensions to avoid circular imports.

MIT License
Copyright (c) 2026 Grade Analysis App
"""

from flask import Flask
from typing import Optional


def init_extensions(app: Flask) -> None:
    """Initialize all Flask extensions.
    
    Args:
        app: Flask application instance.
    """
    # Initialize CSRF protection
    _init_csrf(app)
    
    # Initialize session (using Flask's built-in session)
    _init_session(app)
    
    # Initialize logging
    _init_logging(app)


def _init_csrf(app: Flask) -> None:
    """Initialize CSRF protection.
    
    Args:
        app: Flask application instance.
    """
    from flask_wtf.csrf import CSRFProtect
    
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    # Store csrf in app for later exemption of blueprints
    app.csrf = csrf
    
    # Store csrf_token function for templates
    app.jinja_env.globals['csrf_token'] = lambda: __import__('flask_wtf.csrf', fromlist=['csrf']).csrf.generate_csrf()


def _init_session(app: Flask) -> None:
    """Configure session settings.
    
    Args:
        app: Flask application instance.
    """
    # Flask's default session uses cookies, which is sufficient for this app
    # For production with multiple workers, consider using Flask-Session with Redis/SQL
    pass


def _init_logging(app: Flask) -> None:
    """Configure logging.
    
    Args:
        app: Flask application instance.
    """
    import logging
    import sys
    
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set werkzeug log level
    if not app.debug:
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    app.logger.setLevel(log_level)
    app.logger.info('Application logging initialized')
