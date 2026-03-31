"""Routes Package - Blueprint Registration

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
    from app.routes.rankings import rankings_bp
    from app.routes.statistics import statistics_bp
    from app.routes.trend import trend_bp
    from app.routes.config import config_bp
    
    # Core routes
    app.register_blueprint(main_bp)
    # API routes
    app.register_blueprint(api_bp, url_prefix='/api')
    # Additional modular routes
    app.register_blueprint(rankings_bp, url_prefix='/')
    app.register_blueprint(statistics_bp, url_prefix='/')
    app.register_blueprint(trend_bp, url_prefix='/')
    app.register_blueprint(config_bp, url_prefix='/')
