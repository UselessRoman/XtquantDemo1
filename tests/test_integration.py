# tests/test_integration.py
"""
集成测试
"""

import pytest
import pandas as pd
from unittest.mock import patch
from src.data.market_data import MarketDataManager
from src.analysis.technical import TechnicalIndicators
from src.strategy.strategies import MACDStrategy
from src.backtest.engine import BacktestEngine


class TestIntegration:
    """集成测试"""
    
    @patch('src.data.market_data.xtdata')
    def test_data_to_strategy_flow(self, mock_xtdata, sample_stock_data):
        """测试数据到策略的完整流程"""
        # 模拟数据获取
        mock_xtdata.get_local_data.return_value = {
            '002352.SZ': sample_stock_data
        }
        
        # 获取数据
        data_manager = MarketDataManager()
        data = data_manager.get_local_data('002352.SZ', '1d')
        
        # 计算指标
        calculator = TechnicalIndicators()
        indicators = calculator.calculate_all(data)
        
        # 生成策略信号
        strategy = MACDStrategy()
        signals = strategy.generate_signals(data, indicators)
        
        # 运行回测
        engine = BacktestEngine()
        result = engine.run(data, signals)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
