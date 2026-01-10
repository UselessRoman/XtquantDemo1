# tests/test_config.py
"""
配置模块测试
"""

import pytest
from src.core.config import ChartConfig, BacktestConfig, DataConfig, TradeConfig


class TestChartConfig:
    """测试图表配置"""
    
    def test_chart_config_colors(self):
        """测试颜色配置"""
        config = ChartConfig()
        assert 'up' in config.COLORS
        assert 'down' in config.COLORS
        assert 'ma5' in config.COLORS
        assert isinstance(config.COLORS, dict)
    
    def test_chart_config_font(self):
        """测试字体配置"""
        config = ChartConfig()
        assert 'family' in config.FONT_CONFIG
        assert 'size_title' in config.FONT_CONFIG
        assert isinstance(config.FONT_CONFIG['size_title'], int)
    
    def test_chart_config_indicators(self):
        """测试指标参数配置"""
        config = ChartConfig()
        assert 'ma_periods' in config.INDICATORS
        assert 'macd_fast' in config.INDICATORS
        assert isinstance(config.INDICATORS['ma_periods'], list)


class TestBacktestConfig:
    """测试回测配置"""
    
    def test_backtest_config_values(self):
        """测试回测配置值"""
        assert BacktestConfig.INITIAL_CAPITAL > 0
        assert 0 < BacktestConfig.COMMISSION_RATE < 1
        assert 0 < BacktestConfig.SLIPPAGE_RATE < 1
        assert 0 < BacktestConfig.RISK_FREE_RATE < 1


class TestDataConfig:
    """测试数据配置"""
    
    def test_data_config_defaults(self):
        """测试数据配置默认值"""
        assert DataConfig.DEFAULT_PERIOD == '1d'
        assert len(DataConfig.DEFAULT_START_DATE) == 8


class TestTradeConfig:
    """测试交易配置"""
    
    def test_trade_config_account_type(self):
        """测试账户类型"""
        assert TradeConfig.ACCOUNT_TYPE in ['STOCK', 'CREDIT', 'FUTURE']
    
    def test_trade_config_limits(self):
        """测试交易限制"""
        assert TradeConfig.MIN_ORDER_QUANTITY > 0
        assert TradeConfig.MAX_ORDER_QUANTITY > TradeConfig.MIN_ORDER_QUANTITY
        assert 0 < TradeConfig.MAX_POSITION_RATIO <= 1
        assert 0 < TradeConfig.SINGLE_STOCK_RATIO <= 1
