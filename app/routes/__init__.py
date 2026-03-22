"""
Routes Package - Blueprint Registration

This module registers all blueprints for the Flask application.
"""

from flask import Flask


def register_blueprints(app: Flask) -> None:
    """Register all blueprints with the Flask application.
    
    Args:
        app: Flask application instance.
    """
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
