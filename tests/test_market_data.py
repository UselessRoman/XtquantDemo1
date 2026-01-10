# tests/test_market_data.py
"""
行情数据管理模块测试
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from src.data.market_data import MarketDataManager


class TestMarketDataManager:
    """测试行情数据管理器"""
    
    def test_market_data_manager_init(self):
        """测试初始化"""
        manager = MarketDataManager()
        assert manager is not None
        assert manager.required_columns == ['open', 'high', 'low', 'close', 'volume']
    
    @patch('src.data.market_data.xtdata')
    def test_download_history_data_success(self, mock_xtdata):
        """测试成功下载历史数据"""
        manager = MarketDataManager()
        
        # 模拟返回数据
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        mock_data = pd.DataFrame({
            'open': [100] * 10,
            'high': [105] * 10,
            'low': [95] * 10,
            'close': [100] * 10,
            'volume': [1000000] * 10
        }, index=dates)
        
        mock_xtdata.get_local_data.return_value = {'002352.SZ': mock_data}
        
        result = manager.download_history_data('002352.SZ', '1d', '20240101', '20240110')
        assert result == True
    
    @patch('src.data.market_data.xtdata')
    def test_download_history_data_failure(self, mock_xtdata):
        """测试下载失败"""
        manager = MarketDataManager()
        mock_xtdata.get_local_data.return_value = {'002352.SZ': pd.DataFrame()}
        
        result = manager.download_history_data('002352.SZ', '1d')
        assert result == False
    
    @patch('src.data.market_data.xtdata')
    def test_get_local_data_success(self, mock_xtdata):
        """测试获取本地数据"""
        manager = MarketDataManager()
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        mock_data = pd.DataFrame({
            'open': [100] * 10,
            'high': [105] * 10,
            'low': [95] * 10,
            'close': [100] * 10,
            'volume': [1000000] * 10
        }, index=dates)
        
        mock_xtdata.get_local_data.return_value = {'002352.SZ': mock_data}
        
        result = manager.get_local_data('002352.SZ', '1d')
        assert result is not None
        assert len(result) == 10
    
    @patch('src.data.market_data.xtdata')
    def test_update_data(self, mock_xtdata):
        """测试增量更新数据"""
        manager = MarketDataManager()
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        mock_data = pd.DataFrame({
            'open': [100] * 10,
            'high': [105] * 10,
            'low': [95] * 10,
            'close': [100] * 10,
            'volume': [1000000] * 10
        }, index=dates)
        
        mock_xtdata.get_local_data.return_value = {'002352.SZ': mock_data}
        
        result = manager.update_data('002352.SZ', '1d')
        assert result == True
