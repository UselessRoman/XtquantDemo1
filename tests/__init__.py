# tests/__init__.py
"""
测试模块
"""

# 必须在所有导入之前设置 Python 路径
import sys
import os

# 获取项目根目录
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 确保项目根目录在 Python 路径中（必须最先执行）
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
