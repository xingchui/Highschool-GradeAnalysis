"""
Application Entry Point

This module provides the entry point for running the Flask application
using the new application factory pattern.
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def main():
    """Main entry point for the application."""
    from app import create_app
    from app.config import config_by_name
    
    # Get environment from command line or environment variable
    env = os.environ.get('FLASK_ENV', 'development')
    
    # Create the application
    app = create_app(config_by_name.get(env, config_by_name['development']))
    
    # Print startup info
    print(f"\n{'='*60}")
    print(f"高中成绩分析系统 v2.0.0")
    print(f"环境: {env}")
    print(f"调试模式: {app.debug}")
    print(f"{'='*60}\n")
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.debug
    )


if __name__ == '__main__':
    main()
