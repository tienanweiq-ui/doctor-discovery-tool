# -*- coding: utf-8 -*-
"""
Vercel Serverless Entry Point - Minimal version
医生临床研究画像 · 在线工具
"""
import sys
import os

# 获取项目根目录
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
os.chdir(root_dir)

# 创建最小化 Flask 应用
from flask import Flask, jsonify

app = Flask(__name__)

# 简单路由
@app.route('/')
def index():
    """返回简单的欢迎信息"""
    return jsonify({
        'message': '医生临床研究画像在线工具',
        'status': 'running',
        'version': '1.0'
    })

@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': 'doctor-discovery-tool'
    })

# Vercel 需要导出应用
__all__ = ['app']
