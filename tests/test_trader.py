# tests/test_trader.py
"""
交易模块测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.trading.trader import Trader


class TestTrader:
    """测试交易类"""
    
    def test_trader_init(self):
        """测试初始化"""
        trader = Trader(
            qmt_path=r'D:\test',
            account_id='test123',
            account_type='STOCK'
        )
        assert trader.qmt_path == r'D:\test'
        assert trader.account_id == 'test123'
        assert trader.account_type == 'STOCK'
        assert trader.is_connected == False
