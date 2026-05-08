"""
Application Entry Point

This module provides the entry point for running the Flask application
using the new application factory pattern.
"""

import os
import sys
import threading
import webbrowser

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def _open_browser(port: int, delay: float = 1.5):
    """Open the browser after a short delay to let the server start.
    
    Args:
        port: Port number the server is listening on.
        delay: Seconds to wait before opening browser.
    """
    def _open():
        import time
        time.sleep(delay)
        url = f'http://127.0.0.1:{port}'
        webbrowser.open(url)
    
    thread = threading.Thread(target=_open, daemon=True)
    thread.start()


def main():
    """Main entry point for the application."""
    from app import create_app, __version__
    from app.config import config_by_name
    
    # Get environment from command line or environment variable
    env = os.environ.get('FLASK_ENV', 'development')
    
    # Create the application
    app = create_app(config_by_name.get(env, config_by_name['development']))
    
    # Get the port to use
    port = int(os.environ.get('PORT', 5000))
    
    # Print startup info
    print(f"\n{'='*60}")
    print(f"高中成绩分析系统 v{__version__}")
    print(f"环境: {env}")
    print(f"调试模式: {app.debug}")
    print(f"{'='*60}\n")
    print(f"正在自动打开浏览器...")
    
    # Auto-open browser after server starts
    _open_browser(port)
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.debug,
        use_reloader=False  # 禁用watchdog自动重载，防止Windows上进程异常退出
    )


if __name__ == '__main__':
    main()
