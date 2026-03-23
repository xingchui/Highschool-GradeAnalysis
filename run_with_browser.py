"""
Grade Analysis App - Windows Launcher
自动打开浏览器并启动Flask服务器
"""

import os
import sys
import time
import webbrowser
import threading
from app import create_app
from app.config import DevelopmentConfig


def open_browser(url):
    """延迟打开浏览器"""
    time.sleep(1.5)  # 等待服务器启动
    webbrowser.open(url)


def main():
    """主函数"""
    print("=" * 60)
    print("        高中成绩分析系统 v2.0.0")
    print("=" * 60)
    print()
    print("正在启动服务器...")
    print()
    
    # 创建应用
    app = create_app(DevelopmentConfig())
    
    # 获取端口
    port = int(os.environ.get('PORT', 5000))
    url = f'http://localhost:{port}'
    
    print(f"服务器地址: {url}")
    print()
    print("正在自动打开浏览器...")
    print("如浏览器未自动打开，请手动访问上面的地址")
    print()
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    print()
    
    # 在后台线程中打开浏览器
    browser_thread = threading.Thread(target=open_browser, args=(url,))
    browser_thread.daemon = True
    browser_thread.start()
    
    # 启动服务器
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,  # 生产模式，避免reloader问题
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
    except Exception as e:
        print(f"\n\n错误: {e}")
        print("\n按回车键退出...")
        input()


if __name__ == '__main__':
    main()
