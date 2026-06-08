# -*- coding: utf-8 -*-
"""
Vercel Serverless Entry Point
医生临床研究画像 · 在线工具
"""
import sys
import os

# 获取项目根目录
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# 导入 Flask 应用
try:
    # 首先尝试设置正确的工作目录
    os.chdir(root_dir)

    # 然后导入应用
    from app import app

except Exception as e:
    # 如果导入失败，创建一个简单的错误应用
    from flask import Flask, jsonify
    app = Flask(__name__)

    @app.route('/')
    def error():
        return jsonify({
            'error': f'Failed to import app: {str(e)}',
            'root_dir': root_dir,
            'sys_path': sys.path[:3]
        }), 500

# Vercel 需要导出应用
__all__ = ['app']
