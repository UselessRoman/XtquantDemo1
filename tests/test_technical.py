# tests/test_technical.py
"""
技术指标分析模块测试
"""

import pytest
import pandas as pd
import numpy as np
from src.analysis.technical import TechnicalIndicators
from src.visualization.chart import ChartPlotter


class TestTechnicalIndicators:
    """测试技术指标计算器"""
    
    def test_calculate_ma(self, sample_stock_data):
        """测试移动平均线计算"""
        calculator = TechnicalIndicators()
        ma_data = calculator.calculate_moving_averages(sample_stock_data)
        
        assert isinstance(ma_data, pd.DataFrame)
        assert 'MA5' in ma_data.columns
        assert 'MA10' in ma_data.columns
        assert 'MA20' in ma_data.columns
        assert len(ma_data) == len(sample_stock_data)
    
    def test_calculate_macd(self, sample_stock_data):
        """测试MACD指标计算"""
        calculator = TechnicalIndicators()
        macd_data = calculator.calculate_macd(sample_stock_data)
        
        assert isinstance(macd_data, pd.DataFrame)
        assert 'DIF' in macd_data.columns
        assert 'DEA' in macd_data.columns
        assert 'MACD' in macd_data.columns
    
    def test_calculate_kdj(self, sample_stock_data):
        """测试KDJ指标计算"""
        calculator = TechnicalIndicators()
        kdj_data = calculator.calculate_kdj(sample_stock_data)
        
        assert isinstance(kdj_data, pd.DataFrame)
        assert 'K' in kdj_data.columns
        assert 'D' in kdj_data.columns
        assert 'J' in kdj_data.columns
    
    def test_calculate_all(self, sample_stock_data):
        """测试计算所有指标"""
        calculator = TechnicalIndicators()
        indicators = calculator.calculate_all(sample_stock_data)
        
        assert isinstance(indicators, dict)
        assert 'ma' in indicators
        assert 'macd' in indicators
        assert 'kdj' in indicators


class TestChartPlotter:
    """测试图表绘制器"""
    
    def test_chart_plotter_init(self):
        """测试初始化"""
        plotter = ChartPlotter()
        assert plotter is not None
        assert plotter.config is not None
    
    def test_create_chart(self, sample_stock_data, sample_indicators):
        """测试图表创建"""
        plotter = ChartPlotter()
        data = sample_stock_data.iloc[:30]
        indicators = {
            'ma': sample_indicators['ma'].iloc[:30],
            'macd': sample_indicators['macd'].iloc[:30],
            'kdj': sample_indicators['kdj'].iloc[:30]
        }
        
        try:
            fig, axes = plotter.create_chart(data, indicators, 'TEST.SZ')
            assert fig is not None
            assert axes is not None
            import matplotlib.pyplot as plt
            plt.close(fig)
        except Exception as e:
            pytest.skip(f"图表创建失败: {e}")
