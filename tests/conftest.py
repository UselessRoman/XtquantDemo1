# tests/conftest.py
"""
pytest配置文件
提供测试用的fixtures和共享资源
"""

# 必须在所有其他导入之前设置路径
import sys
import os

# 确保项目根目录在 Python 路径中（必须最先执行）
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_stock_data():
    """生成样本股票数据用于测试"""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    
    # 生成价格数据
    np.random.seed(42)
    base_price = 40.0
    returns = np.random.randn(100) * 0.02
    prices = base_price * (1 + returns).cumprod()
    
    data = pd.DataFrame({
        'open': prices * (1 + np.random.randn(100) * 0.01),
        'high': prices * (1 + np.abs(np.random.randn(100)) * 0.015),
        'low': prices * (1 - np.abs(np.random.randn(100)) * 0.015),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, 100)
    }, index=dates)
    
    # 确保数据有效性
    data['high'] = data[['high', 'open', 'close']].max(axis=1)
    data['low'] = data[['low', 'open', 'close']].min(axis=1)
    
    return data


@pytest.fixture
def sample_stock_data_short():
    """生成短期样本数据（用于快速测试）"""
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    
    np.random.seed(42)
    base_price = 40.0
    returns = np.random.randn(30) * 0.02
    prices = base_price * (1 + returns).cumprod()
    
    data = pd.DataFrame({
        'open': prices * (1 + np.random.randn(30) * 0.01),
        'high': prices * (1 + np.abs(np.random.randn(30)) * 0.015),
        'low': prices * (1 - np.abs(np.random.randn(30)) * 0.015),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, 30)
    }, index=dates)
    
    data['high'] = data[['high', 'open', 'close']].max(axis=1)
    data['low'] = data[['low', 'open', 'close']].min(axis=1)
    
    return data


@pytest.fixture
def sample_indicators(sample_stock_data):
    """生成样本技术指标数据"""
    from src.analysis.technical import TechnicalIndicators
    
    calculator = TechnicalIndicators()
    indicators = calculator.calculate_all(sample_stock_data)
    
    return indicators
