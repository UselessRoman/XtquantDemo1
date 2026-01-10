# tests/test_financial_data.py
"""
财务数据管理模块测试
"""

import pytest
import pandas as pd
from unittest.mock import patch
from src.data.financial_data import FinancialDataManager


class TestFinancialDataManager:
    """测试财务数据管理器"""
    
    def test_financial_data_manager_init(self):
        """测试初始化"""
        manager = FinancialDataManager()
        assert manager is not None
    
    @patch('src.data.financial_data.xtdata')
    def test_download_financial_data_simple(self, mock_xtdata):
        """测试简单下载"""
        manager = FinancialDataManager()
        result = manager.download_financial_data(['600000.SH'])
        assert result == True
        mock_xtdata.download_financial_data.assert_called_once()
    
    @patch('src.data.financial_data.xtdata')
    def test_download_financial_data_with_time(self, mock_xtdata):
        """测试带时间范围的下载"""
        manager = FinancialDataManager()
        result = manager.download_financial_data(
            ['600000.SH'], 
            start_time='20240101',
            end_time='20241231'
        )
        assert result == True
        mock_xtdata.download_financial_data2.assert_called_once()
    
    @patch('src.data.financial_data.xtdata')
    def test_get_financial_data_success(self, mock_xtdata):
        """测试获取财务数据"""
        manager = FinancialDataManager()
        
        mock_income = pd.DataFrame({
            'm_timetag': ['20240630'],
            'revenue': [1000000],
            'net_profit_excl_min_int_inc': [100000]
        })
        mock_balance = pd.DataFrame({
            'm_timetag': ['20240630'],
            'tot_liab_shrhldr_eqy': [5000000]
        })
        mock_pershare = pd.DataFrame({
            'm_timetag': ['20240630'],
            'du_return_on_equity': [10.5],
            's_fa_eps_basic': [0.5]
        })
        
        mock_xtdata.get_financial_data.return_value = {
            '600000.SH': {
                'Income': mock_income,
                'Balance': mock_balance,
                'Pershareindex': mock_pershare
            }
        }
        mock_xtdata.get_market_data.return_value = {
            '600000.SH': pd.Series({'pe': 15.5})
        }
        
        result = manager.get_financial_data('600000.SH', auto_download=False)
        assert result is not None
        assert isinstance(result, dict)
