# fundamental.py
"""
财务指标分析模块
功能：财务指标评分和分析
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict
import warnings

warnings.filterwarnings('ignore')


class FundamentalAnalyzer:
    """财务指标分析器：负责财务数据的评分和分析"""
    
    def __init__(self):
        """初始化财务指标分析器"""
        pass
    
    def calculate_financial_score(self, financial_data: Dict) -> Optional[Dict]:
        """
        计算财务指标得分
        
        Args:
            financial_data: 财务数据字典
            
        Returns:
            Dict: 财务指标得分
        """
        if financial_data is None:
            return None
        
        score = 0
        details = {}
        
        # 1. 市盈率 PE（0-20分）
        pe = financial_data.get('pe')
        if pe is not None and pe > 0:
            if 0 < pe < 15:  # 低PE
                score += 20
                details['pe'] = 'low'
            elif 15 <= pe < 30:
                score += 10
                details['pe'] = 'normal'
            elif pe > 50:
                score -= 10
                details['pe'] = 'high'
        
        # 2. 市净率 PB（0-15分）
        pb = financial_data.get('pb')
        if pb is not None and pb > 0:
            if 0 < pb < 2:
                score += 15
                details['pb'] = 'low'
            elif 2 <= pb < 5:
                score += 8
                details['pb'] = 'normal'
            elif pb > 10:
                score -= 5
                details['pb'] = 'high'
        
        # 3. 净资产收益率 ROE（0-25分）
        roe = financial_data.get('roe')
        if roe is not None:
            if roe > 20:
                score += 25
                details['roe'] = 'excellent'
            elif roe > 15:
                score += 20
                details['roe'] = 'good'
            elif roe > 10:
                score += 15
                details['roe'] = 'normal'
            elif roe > 5:
                score += 8
                details['roe'] = 'low'
        
        # 4. 净利润增长率（0-20分）
        profit_growth = financial_data.get('profit_growth')
        if profit_growth is not None:
            if profit_growth > 30:
                score += 20
                details['profit_growth'] = 'high'
            elif profit_growth > 20:
                score += 15
                details['profit_growth'] = 'good'
            elif profit_growth > 10:
                score += 10
                details['profit_growth'] = 'normal'
            elif profit_growth > 0:
                score += 5
                details['profit_growth'] = 'positive'
        
        # 5. 营业收入增长率（0-20分）
        revenue_growth = financial_data.get('revenue_growth')
        if revenue_growth is not None:
            if revenue_growth > 20:
                score += 20
                details['revenue_growth'] = 'high'
            elif revenue_growth > 10:
                score += 15
                details['revenue_growth'] = 'good'
            elif revenue_growth > 5:
                score += 10
                details['revenue_growth'] = 'normal'
            elif revenue_growth > 0:
                score += 5
                details['revenue_growth'] = 'positive'
        
        return {
            'score': score,
            'max_score': 100,
            'details': details
        }
    
    def filter_financial_data(self, financial_data: Dict, filters: Dict) -> bool:
        """
        根据财务筛选条件过滤数据
        
        Args:
            financial_data: 财务数据字典
            filters: 筛选条件字典
            
        Returns:
            bool: 是否通过筛选
        """
        if financial_data is None:
            return False
        
        # PE筛选
        pe = financial_data.get('pe')
        if 'min_pe' in filters and pe is not None:
            if pe < filters['min_pe']:
                return False
        if 'max_pe' in filters and pe is not None:
            if pe > filters['max_pe']:
                return False
        
        # PB筛选
        pb = financial_data.get('pb')
        if 'min_pb' in filters and pb is not None:
            if pb < filters['min_pb']:
                return False
        if 'max_pb' in filters and pb is not None:
            if pb > filters['max_pb']:
                return False
        
        # ROE筛选
        roe = financial_data.get('roe')
        if 'min_roe' in filters and roe is not None:
            if roe < filters['min_roe']:
                return False
        
        # 净利润增长率筛选
        profit_growth = financial_data.get('profit_growth')
        if 'min_profit_growth' in filters and profit_growth is not None:
            if profit_growth < filters['min_profit_growth']:
                return False
        
        return True
