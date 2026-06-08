# -*- coding: utf-8 -*-
"""
Vercel Serverless Entry Point
医生临床研究画像 · 在线工具
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel 需要导出应用
__all__ = ['app']
