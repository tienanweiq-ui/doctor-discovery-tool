# -*- coding: utf-8 -*-
"""WSGI entry point — re-exports the full Flask app from app.py."""
import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
os.chdir(root_dir)

from app import app  # noqa: E402

__all__ = ["app"]
