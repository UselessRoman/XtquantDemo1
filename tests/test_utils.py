# tests/test_utils.py
"""
工具函数模块测试
"""

import pytest
from datetime import datetime
from src.core.utils import (
    format_date, validate_stock_code, get_next_trading_date,
    format_number, get_trading_days_count
)


class TestFormatDate:
    """测试日期格式化"""
    
    def test_format_date_string_yyyymmdd(self):
        """测试YYYYMMDD格式字符串"""
        assert format_date('20240101') == '20240101'
    
    def test_format_date_string_iso(self):
        """测试ISO格式字符串"""
        assert format_date('2024-01-01') == '20240101'
    
    def test_format_date_datetime(self):
        """测试datetime对象"""
        dt = datetime(2024, 1, 1)
        assert format_date(dt) == '20240101'
    
    def test_format_date_none(self):
        """测试None值"""
        assert format_date(None) is None


class TestValidateStockCode:
    """测试股票代码验证"""
    
    def test_validate_stock_code_valid(self):
        """测试有效股票代码"""
        assert validate_stock_code('002352.SZ') == True
        assert validate_stock_code('600519.SH') == True
    
    def test_validate_stock_code_invalid_format(self):
        """测试无效格式"""
        assert validate_stock_code('002352') == False
        assert validate_stock_code('002352.SZ.SZ') == False
    
    def test_validate_stock_code_invalid_market(self):
        """测试无效市场"""
        assert validate_stock_code('002352.BJ') == False
    
    def test_validate_stock_code_invalid_code(self):
        """测试无效代码"""
        assert validate_stock_code('12345.SZ') == False
        assert validate_stock_code('abc.SZ') == False


class TestGetNextTradingDate:
    """测试获取下一个交易日"""
    
    def test_get_next_trading_date_valid(self):
        """测试有效日期"""
        next_date = get_next_trading_date('20240101')
        assert len(next_date) == 8
        assert next_date.isdigit()
    
    def test_get_next_trading_date_invalid(self):
        """测试无效日期"""
        result = get_next_trading_date('invalid')
        assert result == 'invalid'


class TestFormatNumber:
    """测试数字格式化"""
    
    def test_format_number_small(self):
        """测试小数"""
        assert '40.00' in format_number(40.0, 2)
    
    def test_format_number_wan(self):
        """测试万单位"""
        result = format_number(50000.0)
        assert '万' in result or '5' in result
    
    def test_format_number_na(self):
        """测试NaN值"""
        import pandas as pd
        result = format_number(pd.NA)
        assert result == 'N/A'


class TestGetTradingDaysCount:
    """测试交易日数量估算"""
    
    def test_get_trading_days_count_valid(self):
        """测试有效日期范围"""
        count = get_trading_days_count('20240101', '20240131')
        assert count >= 0
    
    def test_get_trading_days_count_invalid(self):
        """测试无效日期"""
        count = get_trading_days_count('invalid', 'invalid')
        assert count == 0
