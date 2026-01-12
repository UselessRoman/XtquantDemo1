# technical.py
"""
技术指标分析模块
功能：计算技术指标
作者：WJC
日期：2026.1.5
"""

import numpy as np
import pandas as pd
from typing import Dict
import warnings
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.config import ChartConfig

warnings.filterwarnings('ignore')


class TechnicalIndicators:
    """技术指标计算器"""
    
    def __init__(self, config: ChartConfig = None):
        self.config = config or ChartConfig()
    
    def calculate_all(self, data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        计算所有技术指标
        
        Args:
            data: 股票数据
            
        Returns:
            Dict: 包含所有指标的字典
        """
        indicators = {}
        
        # 移动平均线
        indicators['ma'] = self.calculate_moving_averages(data)
        
        # MACD
        indicators['macd'] = self.calculate_macd(data)
        
        # KDJ
        indicators['kdj'] = self.calculate_kdj(data)
        
        return indicators
    
    def calculate_moving_averages(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算移动平均线"""
        ma_data = pd.DataFrame()
        for period in self.config.INDICATORS['ma_periods']:
            ma_data[f'MA{period}'] = data['close'].rolling(window=period).mean()
        return ma_data
    
    def calculate_macd(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算MACD指标"""
        close = data['close']
        
        # 计算EMA
        ema_fast = close.ewm(span=self.config.INDICATORS['macd_fast'], adjust=False).mean()
        ema_slow = close.ewm(span=self.config.INDICATORS['macd_slow'], adjust=False).mean()
        
        # 计算DIF、DEA、MACD
        dif = ema_fast - ema_slow
        dea = dif.ewm(span=self.config.INDICATORS['macd_signal'], adjust=False).mean()
        macd = (dif - dea) * 2  # 传统MACD柱是2倍的(DIF-DEA)
        
        return pd.DataFrame({
            'DIF': dif,
            'DEA': dea,
            'MACD': macd
        })
    
    def calculate_kdj(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算KDJ指标"""
        n = self.config.INDICATORS['kdj_period']
        
        # 计算周期内的最低价和最高价
        low_min = data['low'].rolling(window=n).min()
        high_max = data['high'].rolling(window=n).max()
        
        # 计算RSV
        rsv = 100 * (data['close'] - low_min) / (high_max - low_min + 1e-8)
        
        # 计算K、D、J值
        k = rsv.ewm(com=2, adjust=False).mean()  # 对应3日EMA
        d = k.ewm(com=2, adjust=False).mean()
        j = 3 * k - 2 * d
        
        return pd.DataFrame({
            'K': k,
            'D': d,
            'J': j
        })
