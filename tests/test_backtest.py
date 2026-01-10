# tests/test_backtest.py
"""
回测模块测试
"""

import pytest
import pandas as pd
from src.backtest.engine import BacktestEngine
from src.backtest.analyzer import PerformanceAnalyzer
from src.strategy.strategies import Signal


class TestBacktestEngine:
    """测试回测引擎"""
    
    def test_backtest_engine_init(self):
        """测试初始化"""
        engine = BacktestEngine()
        assert engine.initial_capital == 100000.0
        assert engine.commission_rate == 0.0001
        assert engine.slippage_rate == 0.001
    
    def test_backtest_engine_run(self, sample_stock_data):
        """测试回测执行"""
        engine = BacktestEngine(initial_capital=100000.0)
        signals = pd.Series(0, index=sample_stock_data.index, dtype=int)
        signals.iloc[10] = Signal.BUY.value
        signals.iloc[50] = Signal.SELL.value
        
        result = engine.run(sample_stock_data, signals)
        
        assert isinstance(result, pd.DataFrame)
        assert 'signal' in result.columns
        assert 'position' in result.columns
        assert 'equity' in result.columns
        assert result['equity'].iloc[0] == 100000.0


class TestPerformanceAnalyzer:
    """测试性能分析器"""
    
    def test_performance_analyzer_init(self):
        """测试初始化"""
        analyzer = PerformanceAnalyzer()
        assert analyzer.risk_free_rate == 0.03
    
    def test_performance_analyzer_analyze(self, sample_stock_data):
        """测试性能分析"""
        engine = BacktestEngine()
        analyzer = PerformanceAnalyzer()
        signals = pd.Series(0, index=sample_stock_data.index, dtype=int)
        signals.iloc[10] = Signal.BUY.value
        signals.iloc[50] = Signal.SELL.value
        
        backtest_result = engine.run(sample_stock_data, signals)
        performance = analyzer.analyze(backtest_result)
        
        assert isinstance(performance, dict)
        assert '总收益率' in performance
        assert '年化收益率' in performance
        assert '夏普比率' in performance
