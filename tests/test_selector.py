# tests/test_selector.py
"""
选股模块测试
"""

import pytest
from unittest.mock import patch, Mock
from src.selection.selector import StockSelector


class TestStockSelector:
    """测试选股器"""
    
    def test_stock_selector_init(self):
        """测试初始化"""
        selector = StockSelector()
        assert selector is not None
        assert selector.market_data_manager is not None
        assert selector.financial_data_manager is not None
    
    @patch('src.selection.selector.xtdata')
    def test_get_a_stock_list(self, mock_xtdata):
        """测试获取A股列表"""
        selector = StockSelector()
        mock_xtdata.get_stock_list_in_sector.return_value = [
            '000001.SZ', '600000.SH'
        ]
        
        stock_list = selector.get_a_stock_list()
        assert isinstance(stock_list, list)
        assert len(stock_list) >= 0
