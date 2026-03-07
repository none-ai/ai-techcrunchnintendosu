"""
主程序入口文件
Main Program Entry Point
"""

from app import app

if __name__ == '__main__':
    """
    启动 Flask 应用
    Start Flask Application
    """
    print("=" * 50)
    print("Nintendo 关税诉讼新闻应用启动中...")
    print("Nintendo Tariff Lawsuit News App Starting...")
    print("=" * 50)
    print("\n访问地址: http://localhost:5000\n")

    # 启动应用
    app.run(host='0.0.0.0', port=5000, debug=True)
