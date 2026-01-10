# selector.py
"""
选股模块
功能：基于财务状况和技术指标进行A股选股
"""

from xtquant import xtdata
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.data.market_data import MarketDataManager
from src.data.financial_data import FinancialDataManager
from src.analysis.technical import TechnicalIndicators
from src.analysis.fundamental import FundamentalAnalyzer
from src.core.utils import validate_stock_code

warnings.filterwarnings('ignore')


class StockSelector:
    """A股选股器：基于财务数据和技术指标选股"""
    
    def __init__(self):
        """初始化选股器"""
        self.market_data_manager = MarketDataManager()
        self.financial_data_manager = FinancialDataManager()
        self.indicator_calculator = TechnicalIndicators()
        self.fundamental_analyzer = FundamentalAnalyzer()
    
    def get_a_stock_list(self) -> List[str]:
        """
        获取所有A股股票列表
        
        Returns:
            List[str]: A股股票代码列表
        """
        try:
            # 获取所有A股股票代码
            try:
                stock_list = xtdata.get_stock_list_in_sector('沪深A股')
            except:
                try:
                    stock_list = xtdata.get_stock_list()
                except:
                    # 如果API不可用，返回示例列表
                    print("无法获取股票列表，使用示例列表")
                    stock_list = [
                        '000001.SZ', '000002.SZ', '600000.SH', '600519.SH',
                        '000858.SZ', '002352.SZ', '600036.SH', '000063.SZ'
                    ]
            
            # 过滤A股（确保格式正确）
            a_stocks = []
            for stock in stock_list:
                if isinstance(stock, str) and (stock.endswith('.SZ') or stock.endswith('.SH')):
                    a_stocks.append(stock)
            
            print(f"[成功] 获取到 {len(a_stocks)} 只A股")
            return a_stocks
            
        except Exception as e:
            print(f"[错误] 获取A股列表失败: {e}")
            return []
    
    def get_technical_score(self, stock_code: str, period: str = "1d",
                           lookback_days: int = 60) -> Optional[Dict]:
        """
        计算技术指标得分
        
        Args:
            stock_code: 股票代码
            period: 数据周期
            lookback_days: 回看天数
            
        Returns:
            Dict: 技术指标得分
        """
        try:
            # 获取历史数据
            end_time = datetime.now().strftime('%Y%m%d')
            start_time = (datetime.now() - timedelta(days=lookback_days + 30)).strftime('%Y%m%d')
            
            data = self.market_data_manager.get_local_data(stock_code, period, start_time, end_time)
            
            if data is None or data.empty or len(data) < 20:
                return None
            
            # 计算技术指标
            indicators = self.indicator_calculator.calculate_all(data)
            
            # 获取最新数据
            latest_data = data.iloc[-1]
            latest_ma = indicators['ma'].iloc[-1]
            latest_macd = indicators['macd'].iloc[-1]
            latest_kdj = indicators['kdj'].iloc[-1]
            
            score = 0
            details = {}
            
            # 1. 价格相对均线位置（0-30分）
            if not pd.isna(latest_ma['MA5']) and not pd.isna(latest_ma['MA10']):
                if latest_data['close'] > latest_ma['MA5']:
                    score += 10
                    details['price_vs_ma5'] = 'above'
                if latest_data['close'] > latest_ma['MA10']:
                    score += 10
                    details['price_vs_ma10'] = 'above'
                if latest_data['close'] > latest_ma['MA20']:
                    score += 10
                    details['price_vs_ma20'] = 'above'
            
            # 2. MACD信号（0-20分）
            if not pd.isna(latest_macd['DIF']) and not pd.isna(latest_macd['DEA']):
                if latest_macd['DIF'] > latest_macd['DEA']:
                    score += 10
                    details['macd_signal'] = 'bullish'
                if latest_macd['MACD'] > 0:
                    score += 10
                    details['macd_bar'] = 'positive'
            
            # 3. KDJ信号（0-20分）
            if not pd.isna(latest_kdj['K']) and not pd.isna(latest_kdj['D']):
                k = latest_kdj['K']
                d = latest_kdj['D']
                if 20 < k < 80 and k > d:  # 正常区间且K>D
                    score += 10
                    details['kdj_signal'] = 'normal'
                if k < 30:  # 超卖区域
                    score += 10
                    details['kdj_position'] = 'oversold'
            
            # 4. 成交量（0-15分）
            avg_volume = data['volume'].tail(20).mean()
            if latest_data['volume'] > avg_volume * 1.2:
                score += 15
                details['volume'] = 'increasing'
            
            # 5. 趋势强度（0-15分）
            if len(data) >= 20:
                recent_returns = (data['close'].iloc[-1] / data['close'].iloc[-20] - 1) * 100
                if recent_returns > 5:
                    score += 15
                    details['trend'] = 'strong_up'
                elif recent_returns > 0:
                    score += 8
                    details['trend'] = 'up'
            
            return {
                'score': score,
                'max_score': 100,
                'details': details,
                'latest_price': float(latest_data['close']),
                'ma5': float(latest_ma['MA5']) if not pd.isna(latest_ma['MA5']) else None,
                'ma10': float(latest_ma['MA10']) if not pd.isna(latest_ma['MA10']) else None,
                'ma20': float(latest_ma['MA20']) if not pd.isna(latest_ma['MA20']) else None,
            }
            
        except Exception as e:
            print(f"[错误] 计算 {stock_code} 技术得分失败: {e}")
            return None
    
    def select_stocks(self, 
                     stock_list: List[str] = None,
                     financial_filters: Dict = None,
                     technical_filters: Dict = None,
                     min_total_score: float = 60.0,
                     max_results: int = 50) -> pd.DataFrame:
        """
        选股主函数
        
        Args:
            stock_list: 股票列表，如果为None则获取所有A股
            financial_filters: 财务筛选条件
            technical_filters: 技术筛选条件
            min_total_score: 最小总分（财务+技术）
            max_results: 最大返回结果数
            
        Returns:
            DataFrame: 选股结果
        """
        if stock_list is None:
            stock_list = self.get_a_stock_list()
        
        if not stock_list:
            print("[错误] 股票列表为空")
            return pd.DataFrame()
        
        # 默认筛选条件
        if financial_filters is None:
            financial_filters = {
                'min_pe': 0,
                'max_pe': 50,
                'min_pb': 0,
                'max_pb': 10,
                'min_roe': 5,
                'min_profit_growth': 0
            }
        
        if technical_filters is None:
            technical_filters = {
                'min_technical_score': 30,
                'require_above_ma20': False
            }
        
        results = []
        total = len(stock_list)
        
        print(f"\n开始选股，共 {total} 只股票...")
        print("=" * 60)
        
        for i, stock_code in enumerate(stock_list, 1):
            if i % 100 == 0:
                print(f"进度: {i}/{total} ({i/total*100:.1f}%)")
            
            try:
                # 1. 获取财务数据
                financial_data = self.financial_data_manager.get_financial_data(stock_code)
                
                # 财务筛选
                if not financial_data:
                    continue
                
                # 应用财务筛选条件
                pe = financial_data.get('pe')
                pb = financial_data.get('pb')
                roe = financial_data.get('roe')
                profit_growth = financial_data.get('profit_growth')
                
                if pe is not None:
                    if pe < financial_filters['min_pe'] or pe > financial_filters['max_pe']:
                        continue
                if pb is not None:
                    if pb < financial_filters['min_pb'] or pb > financial_filters['max_pb']:
                        continue
                if roe is not None:
                    if roe < financial_filters['min_roe']:
                        continue
                if profit_growth is not None:
                    if profit_growth < financial_filters['min_profit_growth']:
                        continue
                
                # 2. 计算财务得分
                financial_score_data = self.fundamental_analyzer.calculate_financial_score(financial_data)
                if financial_score_data is None:
                    continue
                
                financial_score = financial_score_data['score']
                
                # 3. 获取技术得分
                technical_score_data = self.get_technical_score(stock_code)
                
                if technical_score_data is None:
                    continue
                
                technical_score = technical_score_data['score']
                
                # 技术筛选
                if technical_score < technical_filters['min_technical_score']:
                    continue
                
                if technical_filters['require_above_ma20']:
                    if technical_score_data.get('ma20') is None:
                        continue
                    if technical_score_data['latest_price'] <= technical_score_data['ma20']:
                        continue
                
                # 4. 计算总分
                total_score = financial_score * 0.6 + technical_score * 0.4
                
                if total_score < min_total_score:
                    continue
                
                # 5. 保存结果
                result = {
                    'stock_code': stock_code,
                    'financial_score': financial_score,
                    'technical_score': technical_score,
                    'total_score': total_score,
                    'pe': financial_data.get('pe'),
                    'pb': financial_data.get('pb'),
                    'roe': financial_data.get('roe'),
                    'profit_growth': financial_data.get('profit_growth'),
                    'revenue_growth': financial_data.get('revenue_growth'),
                    'latest_price': technical_score_data.get('latest_price'),
                    'market_cap': financial_data.get('market_cap'),
                }
                
                results.append(result)
                
            except Exception as e:
                # 跳过出错的股票
                continue
        
        # 转换为DataFrame并排序
        if results:
            df = pd.DataFrame(results)
            df = df.sort_values('total_score', ascending=False)
            df = df.head(max_results)
            
            print(f"\n[成功] 选股完成，共选出 {len(df)} 只股票")
            return df
        else:
            print("\n[错误] 未选出符合条件的股票")
            return pd.DataFrame()
    
    def save_selection_result(self, result_df: pd.DataFrame, filename: str = None):
        """
        保存选股结果
        
        Args:
            result_df: 选股结果DataFrame
            filename: 文件名，如果为None则自动生成
        """
        if result_df.empty:
            print("[错误] 选股结果为空，无法保存")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'stock_selection_{timestamp}.csv'
        
        os.makedirs('./data', exist_ok=True)
        filepath = f'./data/{filename}'
        result_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"[成功] 选股结果已保存: {filepath}")
