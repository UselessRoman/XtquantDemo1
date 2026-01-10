# tests/test_auto_trader.py
"""
自动交易模块测试
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.trading.auto_trader import AutoTrader


class TestAutoTrader:
    """测试自动交易类"""
    
    def test_auto_trader_init(self):
        """测试初始化"""
        mock_trader = MagicMock()
        mock_trader.is_connected = True
        
        auto_trader = AutoTrader(trader=mock_trader)
        assert auto_trader.trader is not None
