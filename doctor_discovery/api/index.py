# -*- coding: utf-8 -*-
"""
Vercel Serverless Entry Point
医生临床研究画像 · 在线工具
"""
import sys
import os
import traceback

# 获取项目根目录
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# 创建基础 Flask 应用
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

app = Flask(__name__, template_folder=os.path.join(root_dir, 'templates'))
CORS(app)

error_message = None

# 尝试导入 doctor_discovery 模块
try:
    os.chdir(root_dir)
    from doctor_discovery import pubmed_client, parse, classify, quality, identity, profile
    modules_loaded = True
except Exception as e:
    modules_loaded = False
    error_message = f"Failed to load doctor_discovery: {str(e)}\n\n{traceback.format_exc()}"
    print(error_message)

# 定义路由
@app.route('/')
def index():
    """主页"""
    try:
        return render_template('index.html')
    except Exception as e:
        return jsonify({'error': f'Failed to load template: {str(e)}'}), 500

@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'modules_loaded': modules_loaded,
        'error': error_message
    })

@app.route('/api/search', methods=['POST'])
def search_doctor():
    """搜索医生"""
    if not modules_loaded:
        return jsonify({
            'success': False,
            'error': 'Modules not loaded. See /api/health for details.'
        }), 500

    # 这里放原来的搜索逻辑
    return jsonify({
        'success': False,
        'error': 'Not implemented yet'
    }), 501

# Vercel 需要导出应用
__all__ = ['app']
