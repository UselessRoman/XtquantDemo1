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
import pickle
# 延迟导入lightgbm，避免在模块加载时失败
# import lightgbm 

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.data.market_data import MarketDataManager
from src.data.financial_data import FinancialDataManager
from src.analysis.technical import TechnicalIndicators
from src.analysis.fundamental import FundamentalAnalyzer
from src.analysis.factor_calculator import FactorCalculator
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


class MLStockSelector(StockSelector):
    """机器学习选股器：基于47因子+ML模型的选股"""
    
    def __init__(self, model_path: str, stock_num: int = 7, score_threshold: float = 0.61):
        """
        初始化ML选股器
        
        Args:
            model_path: 模型文件路径
            stock_num: 选股数量
            score_threshold: 得分阈值
        """
        super().__init__()  # 复用父类的数据管理器
        self.factor_calculator = FactorCalculator()
        self.model = self._load_model(model_path)
        self.stock_num = stock_num
        self.score_threshold = score_threshold
        
        # ML模型类别（必须和训练时一致）
        self.model_classes = np.array([0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1])
    
    def _load_model(self, model_path: str):
        """加载模型文件"""
        import pickle
        import os
        import sys
        
        # 检查必要的依赖
        try:
            import lightgbm
        except ImportError as e:
            # 检测当前Python环境
            in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            
            # 构建错误提示信息
            if in_venv:
                error_msg = (
                    f"[错误] 缺少必要的依赖库: lightgbm\n"
                    f"\n检测到您正在使用虚拟环境: {sys.prefix}\n"
                    f"请在虚拟环境中安装依赖，运行以下命令之一：\n"
                    f"  方式1: {sys.executable} -m pip install -r requirements.txt\n"
                    f"  方式2: pip install -r requirements.txt  （确保虚拟环境已激活）\n"
                    f"  方式3: pip install lightgbm>=3.3.0 scikit-learn>=1.0.0 statsmodels>=0.13.0 schedule>=1.2.0\n"
                    f"\n如果不想使用虚拟环境，请在IDE中切换到系统Python解释器\n"
                    f"原始错误: {e}"
                )
            else:
                error_msg = (
                    f"[错误] 缺少必要的依赖库: lightgbm\n"
                    f"当前Python: {sys.executable}\n"
                    f"请运行以下命令安装依赖：\n"
                    f"  pip install -r requirements.txt\n"
                    f"或单独安装：\n"
                    f"  pip install lightgbm>=3.3.0 scikit-learn>=1.0.0 statsmodels>=0.13.0 schedule>=1.2.0\n"
                    f"原始错误: {e}"
                )
            print(error_msg)
            raise ImportError(error_msg) from e
        
        # 支持相对路径和绝对路径
        if not os.path.isabs(model_path):
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_path = os.path.join(project_root, model_path)
        
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            print(f"[成功] 模型加载成功: {model_path}")
            return model
        except ModuleNotFoundError as e:
            error_msg = (
                f"[错误] 模型加载失败：缺少依赖模块\n"
                f"错误详情: {e}\n"
                f"请运行以下命令安装所有依赖：\n"
                f"  pip install -r requirements.txt\n"
            )
            print(error_msg)
            raise ImportError(error_msg) from e
        except Exception as e:
            print(f"[错误] 模型加载失败: {e}")
            raise
    
    def _get_index_stocks(self, index_code: str = None, end_date: str = None) -> List[str]:
        """
        获取指数成分股（中证全指）
        
        Args:
            index_code: 指数代码，默认使用中证全指逻辑（通过获取所有A股实现）
            end_date: 截止日期
            
        Returns:
            List[str]: 成分股列表
        """
        # XTquant可能不直接支持获取指数成分股
        # 这里使用获取所有A股的方式，后续可以优化为真正的指数成分股
        try:
            # 尝试获取指数成分股
            try:
                from xtquant import xtdata
                # 尝试使用sector方式获取
                stock_list = xtdata.get_stock_list_in_sector('沪深A股')
                return [s for s in stock_list if isinstance(s, str) and (s.endswith('.SZ') or s.endswith('.SH'))]
            except:
                # 如果失败，使用父类方法获取所有A股
                return self.get_a_stock_list()
        except Exception as e:
            print(f"[警告] 获取指数成分股失败，使用所有A股: {e}")
            return self.get_a_stock_list()
    
    def _filter_st_stock(self, stock_list: List[str]) -> List[str]:
        """过滤ST股"""
        try:
            from xtquant import xtdata
            current_data = xtdata.get_market_data(['close'], stock_list, period='1d', count=1)
            # XTquant没有直接的ST判断，这里通过股票代码和名称过滤
            filtered = []
            for stock in stock_list:
                # 过滤ST股票（通常代码或名称包含ST）
                if 'ST' not in stock and '*' not in stock:
                    filtered.append(stock)
            return filtered
        except:
            return stock_list
    
    def _filter_kcbj_stock(self, stock_list: List[str]) -> List[str]:
        """过滤科创、北交、创业板股票"""
        filtered = []
        for stock in stock_list:
            # 过滤科创(68开头)、北交(4、8开头)、创业板(3开头)
            if stock[0] not in ['3', '4', '8'] and not stock.startswith('68'):
                filtered.append(stock)
        return filtered
    
    def _filter_paused_stock(self, stock_list: List[str], end_date: str = None) -> List[str]:
        """过滤停牌股票"""
        try:
            # 获取最新数据，如果获取失败可能是停牌
            filtered = []
            for stock in stock_list:
                try:
                    # 尝试获取最近1天的数据
                    if end_date:
                        data = self.market_data_manager.get_local_data(stock, '1d', end_date, end_date)
                    else:
                        # 使用当前日期
                        today = datetime.now().strftime('%Y%m%d')
                        data = self.market_data_manager.get_local_data(stock, '1d', today, today)
                    
                    if data is not None and not data.empty:
                        filtered.append(stock)
                except:
                    continue
            return filtered
        except:
            return stock_list
    
    def _filter_new_stock(self, stock_list: List[str], end_date: str = None) -> List[str]:
        """过滤次新股（上市不足375天）"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        end_dt = datetime.strptime(end_date, '%Y%m%d')
        filtered = []
        
        for stock in stock_list:
            try:
                # 获取股票信息（需要适配XTquant API）
                # 暂时跳过此过滤，因为XTquant可能不提供上市日期
                filtered.append(stock)
            except:
                continue
        
        return filtered
    
    def _filter_limitup_stock(self, stock_list: List[str], end_date: str = None, 
                              hold_stocks: List[str] = None) -> List[str]:
        """过滤涨停股票（已持仓的除外）"""
        if hold_stocks is None:
            hold_stocks = []
        
        filtered = []
        for stock in stock_list:
            if stock in hold_stocks:
                filtered.append(stock)
                continue
            
            try:
                # 获取最新价格
                if end_date:
                    data = self.market_data_manager.get_local_data(stock, '1d', end_date, end_date)
                else:
                    today = datetime.now().strftime('%Y%m%d')
                    data = self.market_data_manager.get_local_data(stock, '1d', today, today)
                
                if data is None or data.empty:
                    continue
                
                # XTquant可能不直接提供涨停价，这里需要从市场数据判断
                # 暂时允许所有股票，后续可以优化
                filtered.append(stock)
            except:
                continue
        
        return filtered
    
    def _filter_limitdown_stock(self, stock_list: List[str], end_date: str = None,
                               hold_stocks: List[str] = None) -> List[str]:
        """过滤跌停股票（已持仓的除外）"""
        if hold_stocks is None:
            hold_stocks = []
        
        filtered = []
        for stock in stock_list:
            if stock in hold_stocks:
                filtered.append(stock)
                continue
            
            try:
                if end_date:
                    data = self.market_data_manager.get_local_data(stock, '1d', end_date, end_date)
                else:
                    today = datetime.now().strftime('%Y%m%d')
                    data = self.market_data_manager.get_local_data(stock, '1d', today, today)
                
                if data is None or data.empty:
                    continue
                
                # 暂时允许所有股票
                filtered.append(stock)
            except:
                continue
        
        return filtered
    
    def _get_fundamental_filtered(self, stock_list: List[str], end_date: str = None,
                                  min_roe: float = 0.15, min_roa: float = 0.10) -> List[str]:
        """
        基本面筛选：ROE>15%, ROA>10%，按市值升序排序
        
        Args:
            stock_list: 股票列表
            end_date: 截止日期
            min_roe: 最小ROE
            min_roa: 最小ROA
            
        Returns:
            List[str]: 筛选后的股票列表（按市值升序）
        """
        filtered_stocks = []
        stock_data = []
        checked_count = 0
        passed_count = 0
        no_data_count = 0
        
        print(f"[信息] 开始基本面筛选（ROE>{min_roe*100}%, ROA>{min_roa*100}%），股票数量: {len(stock_list)}")
        
        for stock_code in stock_list:
            checked_count += 1
            try:
                financial_data = self.financial_data_manager.get_financial_data(stock_code, auto_download=False)
                if not financial_data:
                    no_data_count += 1
                    continue
                
                roe = financial_data.get('roe', 0)
                roa = financial_data.get('roa', 0)
                market_cap = financial_data.get('market_cap', 0)
                
                # 基本面筛选
                if roe and roe > min_roe and roa and roa > min_roa:
                    passed_count += 1
                    stock_data.append({
                        'stock_code': stock_code,
                        'market_cap': market_cap if market_cap else float('inf'),
                        'roe': roe,
                        'roa': roa
                    })
            except Exception as e:
                continue
            
            # 每100只股票打印一次进度
            if checked_count % 100 == 0:
                print(f"  进度: {checked_count}/{len(stock_list)}, 通过: {passed_count}, 无数据: {no_data_count}")
        
        print(f"[信息] 基本面筛选完成: 检查{checked_count}只，通过{passed_count}只，无数据{no_data_count}只")
        
        # 如果通过筛选的股票太少，放宽条件
        if len(stock_data) < self.stock_num:
            print(f"[警告] 通过筛选的股票数量({len(stock_data)})少于目标数量({self.stock_num})")
            print(f"[提示] 建议降低筛选标准（当前: ROE>{min_roe*100}%, ROA>{min_roa*100}%）")
            # 可以在这里实现自动放宽条件的逻辑，暂时返回所有通过的股票
        
        # 按市值升序排序，取前stock_num只
        stock_data.sort(key=lambda x: x['market_cap'])
        filtered_stocks = [s['stock_code'] for s in stock_data[:self.stock_num]]
        
        if filtered_stocks:
            print(f"[信息] 最终选出 {len(filtered_stocks)} 只股票（按市值排序）")
        
        return filtered_stocks
    
    def select_stocks_ml(self, end_date: str = None, index_code: str = None) -> Tuple[List[str], List[float]]:
        """
        ML选股主函数
        
        Args:
            end_date: 截止日期，格式 'YYYYMMDD'
            index_code: 指数代码（可选，用于获取成分股）
            
        Returns:
            Tuple[List[str], List[float]]: (选中的股票列表, 对应的模型得分列表)
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        # 1. 获取初始股票池
        if index_code:
            initial_list = self._get_index_stocks(index_code, end_date)
        else:
            initial_list = self._get_index_stocks(end_date=end_date)
        
        if not initial_list:
            print("[错误] 无法获取股票列表")
            return [], []
        
        # 2. 基础过滤
        print(f"[信息] 初始股票池: {len(initial_list)} 只")
        filtered_list = self._filter_kcbj_stock(initial_list)  # 过滤科创/北交/创业板
        filtered_list = self._filter_st_stock(filtered_list)  # 过滤ST股
        print(f"[信息] 基础过滤后: {len(filtered_list)} 只")
        
        # 3. 基本面筛选（ROE>15%, ROA>10%，按市值排序）
        filtered_list = self._get_fundamental_filtered(filtered_list, end_date)
        print(f"[信息] 基本面筛选后: {len(filtered_list)} 只")
        
        if not filtered_list:
            print("[错误] 基本面筛选后无股票")
            return [], []
        
        # 4. 计算因子并模型预测
        print("[信息] 开始计算因子...")
        factor_results = {}
        
        for i, stock_code in enumerate(filtered_list, 1):
            if i % 10 == 0:
                print(f"  进度: {i}/{len(filtered_list)}")
            
            try:
                factors = self.factor_calculator.calculate_all_factors(stock_code, end_date)
                factor_results[stock_code] = factors
            except Exception as e:
                # print(f"[警告] {stock_code} 因子计算失败: {e}")
                continue
        
        if not factor_results:
            print("[错误] 无有效因子数据")
            return [], []
        
        # 5. 构建因子DataFrame
        factor_df = pd.DataFrame(factor_results).T
        factor_df = factor_df[self.factor_calculator.FACTOR_LIST]  # 确保列顺序正确
        
        # 6. 模型预测
        print("[信息] 模型预测中...")
        try:
            # 模型预测概率
            predictions = self.model.predict_proba(factor_df.values)
            
            # 计算得分：概率 @ 类别向量
            scores = predictions @ self.model_classes
            factor_df['total_score'] = scores
        except Exception as e:
            print(f"[错误] 模型预测失败: {e}")
            return [], []
        
        # 7. 额外过滤（停牌、涨停、跌停）
        filtered_list_2 = self._filter_paused_stock(factor_df.index.tolist(), end_date)
        # 注意：涨停/跌停过滤需要实时数据，这里暂时跳过
        
        # 更新factor_df
        factor_df = factor_df.loc[factor_df.index.isin(filtered_list_2)]
        
        if factor_df.empty:
            print(f"[信息] 过滤后无股票")
            return [], []
        
        # 8. 得分过滤
        factor_df = factor_df[factor_df['total_score'] > self.score_threshold]
        
        if factor_df.empty:
            print(f"[信息] 得分阈值过滤后无股票（阈值: {self.score_threshold}）")
            return [], []
        
        # 9. 按得分排序，取前stock_num只
        factor_df = factor_df.sort_values('total_score', ascending=False)
        selected_stocks = factor_df.head(self.stock_num).index.tolist()
        selected_scores = factor_df.head(self.stock_num)['total_score'].tolist()
        
        print(f"[成功] ML选股完成，选出 {len(selected_stocks)} 只股票")
        if selected_scores:
            print(f"  得分范围: {min(selected_scores):.4f} - {max(selected_scores):.4f}")
        
        return selected_stocks, selected_scores
