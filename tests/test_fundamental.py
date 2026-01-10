# tests/test_fundamental.py
"""
财务指标分析模块测试
"""

import pytest
from src.analysis.fundamental import FundamentalAnalyzer


class TestFundamentalAnalyzer:
    """测试财务指标分析器"""
    
    def test_calculate_financial_score_excellent(self):
        """测试优秀财务得分"""
        analyzer = FundamentalAnalyzer()
        financial_data = {
            'pe': 12.0,
            'pb': 1.5,
            'roe': 25.0,
            'profit_growth': 35.0,
            'revenue_growth': 25.0
        }
        
        result = analyzer.calculate_financial_score(financial_data)
        assert result is not None
        assert result['score'] > 80
        assert result['max_score'] == 100
    
    def test_calculate_financial_score_poor(self):
        """测试较差财务得分"""
        analyzer = FundamentalAnalyzer()
        financial_data = {
            'pe': 60.0,
            'pb': 12.0,
            'roe': 3.0,
            'profit_growth': -5.0
        }
        
        result = analyzer.calculate_financial_score(financial_data)
        assert result is not None
        assert result['score'] < 50
    
    def test_filter_financial_data_pass(self):
        """测试财务数据筛选通过"""
        analyzer = FundamentalAnalyzer()
        financial_data = {
            'pe': 20.0,
            'pb': 3.0,
            'roe': 15.0
        }
        filters = {
            'max_pe': 30,
            'min_roe': 10
        }
        
        result = analyzer.filter_financial_data(financial_data, filters)
        assert result == True
    
    def test_filter_financial_data_fail(self):
        """测试财务数据筛选失败"""
        analyzer = FundamentalAnalyzer()
        financial_data = {'pe': 50.0}
        filters = {'max_pe': 30}
        
        result = analyzer.filter_financial_data(financial_data, filters)
        assert result == False
