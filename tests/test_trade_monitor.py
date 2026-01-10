# tests/test_trade_monitor.py
"""
交易监控模块测试
"""

import pytest
from src.trading.trade_monitor import TradeMonitor


class TestTradeMonitor:
    """测试交易监控器"""
    
    def test_trade_monitor_init(self):
        """测试初始化"""
        monitor = TradeMonitor()
        assert monitor is not None
        assert isinstance(monitor.pending_orders, dict)
        assert isinstance(monitor.confirmed_orders, dict)
    
    def test_register_order(self):
        """测试注册订单"""
        monitor = TradeMonitor()
        monitor.register_order(12345, '600000.SH', 'BUY', 1000, 10.5)
        
        assert 12345 in monitor.pending_orders
        assert monitor.stats['total_requests'] == 1
