"""
Flask Extensions Initialization

This module initializes Flask extensions to avoid circular imports.
"""

from flask import Flask
from typing import Optional


# Extension instances (will be initialized in init_extensions)
# Using lazy initialization to avoid circular imports


def init_extensions(app: Flask) -> None:
    """Initialize all Flask extensions.
    
    Args:
        app: Flask application instance.
    """
    # Initialize session (using Flask's built-in session)
    _init_session(app)
    
    # Initialize logging
    _init_logging(app)


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
