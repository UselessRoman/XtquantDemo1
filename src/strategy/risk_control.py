# risk_control.py
"""
风控模块
功能：RSRS择时、ATR动态止损、市场宽度计算
作者：WJC
日期：2026.1.12
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple
import warnings
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.data.market_data import MarketDataManager

try:
    import statsmodels.api as sm
    from statsmodels.regression.linear_model import WLS
except ImportError:
    print("[警告] statsmodels未安装，RSRS计算功能将不可用")
    sm = None
    WLS = None

warnings.filterwarnings('ignore')


class RiskController:
    """风控控制器：RSRS择时、ATR止损、市场宽度"""
    
    def __init__(self, atr_period: int = 14, atr_multiplier: float = 2.0):
        """
        初始化风控控制器
        
        Args:
            atr_period: ATR计算周期
            atr_multiplier: ATR倍数（止损位 = 最高价 - atr_multiplier * ATR）
        """
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.market_data_manager = MarketDataManager()
        self.stock_highs = {}  # 记录持仓股票的最高价
        
    def calculate_rsrs(self, stock_code: str, end_date: str = None, 
                      n: int = 18, m: int = 600) -> float:
        """
        计算个股RSRS指标
        
        Args:
            stock_code: 股票代码
            end_date: 截止日期，格式 'YYYYMMDD'，None表示使用当前日期
            n: 滚动窗口大小
            m: 历史窗口大小（用于计算均值和标准差）
            
        Returns:
            float: RSRS值
        """
        if sm is None or WLS is None:
            return 0.0
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        # 获取历史数据
        start_date = (datetime.strptime(end_date, '%Y%m%d') - timedelta(days=m + n + 60)).strftime('%Y%m%d')
        data = self.market_data_manager.get_local_data(stock_code, '1d', start_date, end_date)
        
        if data is None or len(data) < n + m:
            return 0.0
        
        # 获取成交量（用于加权）
        volumes = data['volume'].values if 'volume' in data.columns else np.ones(len(data))
        
        # 数据清洗
        data = data.copy()
        data.replace([np.inf, -np.inf], np.nan, inplace=True)
        data = data.dropna()
        
        if len(data) < n:
            return 0.0
        
        highs = data['high'].values
        lows = data['low'].values
        
        if len(volumes) != len(highs):
            volumes = np.ones(len(highs))
        
        betas = []
        r2_list = []
        
        # 滑动窗口计算
        for i in range(len(highs) - n + 1):
            window_highs = highs[i:i+n]
            window_lows = lows[i:i+n]
            
            # 窗口有效性检查
            if np.any(np.isnan(window_highs)) or np.any(np.isnan(window_lows)):
                continue
            if np.all(window_highs == window_highs[0]) or np.all(window_lows == window_lows[0]):
                continue
            
            # 加权最小二乘法回归
            X = sm.add_constant(window_lows)
            weights = volumes[i:i+n] / np.sum(volumes[i:i+n]) if np.sum(volumes[i:i+n]) > 0 else None
            
            try:
                if weights is not None:
                    model = sm.WLS(window_highs, X, weights=weights)
                else:
                    model = sm.OLS(window_highs, X)
                result = model.fit()
                betas.append(result.params[1])
                r2_list.append(result.rsquared)
            except:
                continue
        
        # 结果计算
        if len(betas) == 0:
            return 0.0
        
        current_beta = betas[-1]
        current_r2 = r2_list[-1]
        
        # 动态调整窗口大小
        valid_m = min(m, len(betas))
        mu = np.mean(betas[-valid_m:])
        sigma = np.std(betas[-valid_m:])
        
        if sigma == 0:
            return 0.0
        
        z_score = (current_beta - mu) / sigma
        rsrs = z_score * current_r2 * current_beta
        
        return float(rsrs)
    
    def calculate_market_rsrs(self, end_date: str = None, 
                             index_code: str = '000300.SH',
                             n: int = 18, m: int = 200) -> float:
        """
        计算大盘RSRS（用于市场择时）
        
        Args:
            end_date: 截止日期
            index_code: 指数代码，默认沪深300
            n: 滚动窗口大小
            m: 历史窗口大小
            
        Returns:
            float: 市场RSRS值
        """
        return self.calculate_rsrs(index_code, end_date, n, m)
    
    def calculate_atr(self, stock_code: str, end_date: str = None) -> float:
        """
        计算ATR（平均真实波幅）
        
        Args:
            stock_code: 股票代码
            end_date: 截止日期
            
        Returns:
            float: ATR值
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        start_date = (datetime.strptime(end_date, '%Y%m%d') - timedelta(days=self.atr_period + 30)).strftime('%Y%m%d')
        data = self.market_data_manager.get_local_data(stock_code, '1d', start_date, end_date)
        
        if data is None or len(data) < self.atr_period + 1:
            return 0.0
        
        # 计算真实波幅(TR)
        high = data['high'].iloc[-self.atr_period:]
        low = data['low'].iloc[-self.atr_period:]
        prev_close = data['close'].iloc[-self.atr_period-1:-1]
        
        tr1 = high - low
        tr2 = abs(high - prev_close.shift(1))
        tr3 = abs(low - prev_close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.mean()
        
        return float(atr) if not pd.isna(atr) else 0.0
    
    def calculate_stop_loss_level(self, stock_code: str, current_high: float, 
                                  end_date: str = None) -> float:
        """
        计算动态止损位
        
        Args:
            stock_code: 股票代码
            current_high: 当前最高价
            end_date: 截止日期
            
        Returns:
            float: 止损位价格
        """
        atr = self.calculate_atr(stock_code, end_date)
        stop_loss = current_high - self.atr_multiplier * atr
        return max(0.0, float(stop_loss))
    
    def update_stock_high(self, stock_code: str, current_high: float, 
                         initial_price: float = None):
        """
        更新股票最高价记录
        
        Args:
            stock_code: 股票代码
            current_high: 当前最高价
            initial_price: 初始价格（首次记录时使用）
        """
        if stock_code not in self.stock_highs:
            self.stock_highs[stock_code] = initial_price if initial_price else current_high
        else:
            self.stock_highs[stock_code] = max(self.stock_highs[stock_code], current_high)
    
    def get_stock_high(self, stock_code: str) -> float:
        """获取股票历史最高价"""
        return self.stock_highs.get(stock_code, 0.0)
    
    def clear_stock_high(self, stock_code: str):
        """清除股票最高价记录"""
        if stock_code in self.stock_highs:
            del self.stock_highs[stock_code]
    
    def check_stop_loss(self, stock_code: str, current_price: float, 
                       position_cost: float = None, end_date: str = None) -> Tuple[bool, float]:
        """
        检查是否触发止损
        
        Args:
            stock_code: 股票代码
            current_price: 当前价格
            position_cost: 持仓成本（用于初始化最高价）
            end_date: 截止日期
            
        Returns:
            Tuple[bool, float]: (是否触发止损, 止损位价格)
        """
        # 更新最高价
        if stock_code not in self.stock_highs and position_cost:
            self.update_stock_high(stock_code, position_cost, position_cost)
        else:
            self.update_stock_high(stock_code, current_price)
        
        current_high = self.get_stock_high(stock_code)
        if current_high == 0:
            return False, 0.0
        
        # 计算止损位
        stop_loss_level = self.calculate_stop_loss_level(stock_code, current_high, end_date)
        
        # 检查是否触发
        triggered = current_price <= stop_loss_level
        
        return triggered, stop_loss_level
    
    def calculate_market_breadth(self, end_date: str = None, 
                                index_code: str = '399101.SZ',
                                count: int = 20) -> float:
        """
        计算市场宽度（中证全指成分股行业20日均线占比均值）
        
        注意：由于XTquant可能不直接支持获取行业分类，此实现为简化版本
        通过计算所有A股中20日均线上方的股票占比来近似市场宽度
        
        Args:
            end_date: 截止日期
            index_code: 指数代码（未使用，保留接口兼容性）
            count: 计算周期（20日）
            
        Returns:
            float: 市场宽度（0-100）
        """
        try:
            if end_date is None:
                end_date = datetime.now().strftime('%Y%m%d')
            
            # 获取A股列表（作为中证全指的近似）
            try:
                from xtquant import xtdata
                stock_list = xtdata.get_stock_list_in_sector('沪深A股')
                if not stock_list:
                    # 如果失败，尝试获取部分A股样本
                    stock_list = []
                    for code in ['600000', '000001', '000002', '600036', '600519', '000858', '002415', '300015']:
                        stock_list.extend([f'{code}.SH', f'{code}.SZ'])
                    stock_list = [s for s in stock_list if s.endswith('.SZ') or s.endswith('.SH')]
            except:
                # 如果无法获取，使用样本股票
                stock_list = ['600000.SH', '000001.SZ', '000002.SZ', '600036.SH', '600519.SH']
            
            if not stock_list:
                print("[警告] 无法获取股票列表，使用默认市场宽度")
                return 50.0
            
            # 限制股票数量以提高计算速度（可以后续优化）
            stock_list = stock_list[:500] if len(stock_list) > 500 else stock_list
            
            # 获取所有股票的20日均线数据
            start_date = (datetime.strptime(end_date, '%Y%m%d') - timedelta(days=count + 30)).strftime('%Y%m%d')
            
            above_ma20_count = 0
            valid_count = 0
            
            for stock_code in stock_list:
                try:
                    data = self.market_data_manager.get_local_data(stock_code, '1d', start_date, end_date)
                    if data is None or len(data) < count:
                        continue
                    
                    # 计算20日均线
                    ma20 = data['close'].rolling(window=count).mean().iloc[-1]
                    current_price = data['close'].iloc[-1]
                    
                    if not pd.isna(ma20) and current_price > ma20:
                        above_ma20_count += 1
                    valid_count += 1
                    
                except:
                    continue
            
            if valid_count == 0:
                print("[警告] 无有效股票数据，使用默认市场宽度")
                return 50.0
            
            # 计算市场宽度（20日均线上方的股票占比 * 100）
            market_breadth = (above_ma20_count / valid_count) * 100
            
            print(f"[市场宽度] 有效股票: {valid_count}, 20日均线上方: {above_ma20_count}, 市场宽度: {market_breadth:.2f}")
            return float(market_breadth)
            
        except Exception as e:
            print(f"[错误] 计算市场宽度失败: {e}")
            return 50.0  # 默认市场宽度
    
    def _get_index_stocks(self, index_code: str, end_date: str) -> list:
        """
        获取指数成分股（需要实现）
        
        Args:
            index_code: 指数代码
            end_date: 截止日期
            
        Returns:
            list: 成分股列表
        """
        # TODO: 实现指数成分股获取
        # 方案1: 使用 xtdata.get_stock_list_in_sector() 如果支持
        # 方案2: 手动维护成分股列表
        # 方案3: 从外部数据源获取
        return []
    
    def check_market_timing(self, end_date: str = None, 
                           market_rsrs_threshold: float = -0.9) -> bool:
        """
        检查市场择时（是否允许开仓）
        
        Args:
            end_date: 截止日期
            market_rsrs_threshold: 市场RSRS阈值，低于此值禁止开仓
            
        Returns:
            bool: True表示允许开仓，False表示禁止开仓
        """
        market_rsrs = self.calculate_market_rsrs(end_date)
        if market_rsrs < market_rsrs_threshold:
            return False
        return True
