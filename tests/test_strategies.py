# tests/test_strategies.py
"""
策略模块测试
"""

import pytest
import pandas as pd
from src.strategy.strategies import Signal, MACDStrategy, MAStrategy, KDJStrategy, SignalGenerator


class TestSignal:
    """测试交易信号枚举"""
    
    def test_signal_values(self):
        """测试信号值"""
        assert Signal.BUY.value == 1
        assert Signal.SELL.value == -1
        assert Signal.HOLD.value == 0


class TestMACDStrategy:
    """测试MACD策略"""
    
    def test_macd_strategy_init(self):
        """测试初始化"""
        strategy = MACDStrategy()
        assert strategy is not None
    
    def test_macd_strategy_generate_signals(self, sample_stock_data, sample_indicators):
        """测试生成信号"""
        strategy = MACDStrategy()
        signals = strategy.generate_signals(sample_stock_data, sample_indicators)
        
        assert isinstance(signals, pd.Series)
        assert len(signals) == len(sample_stock_data)
        assert signals.dtype == int


class TestMAStrategy:
    """测试均线策略"""
    
    def test_ma_strategy_init(self):
        """测试初始化"""
        strategy = MAStrategy()
        assert strategy is not None
    
    def test_ma_strategy_generate_signals(self, sample_stock_data, sample_indicators):
        """测试生成信号"""
        strategy = MAStrategy()
        signals = strategy.generate_signals(sample_stock_data, sample_indicators)
        
        assert isinstance(signals, pd.Series)
        assert len(signals) == len(sample_stock_data)


class TestKDJStrategy:
    """测试KDJ策略"""
    
    def test_kdj_strategy_init(self):
        """测试初始化"""
        strategy = KDJStrategy()
        assert strategy is not None
    
    def test_kdj_strategy_generate_signals(self, sample_stock_data, sample_indicators):
        """测试生成信号"""
        strategy = KDJStrategy()
        signals = strategy.generate_signals(sample_stock_data, sample_indicators)
        
        assert isinstance(signals, pd.Series)
        assert len(signals) == len(sample_stock_data)
