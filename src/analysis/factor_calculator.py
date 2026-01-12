# factor_calculator.py
"""
多因子计算模块
功能：计算47个量化因子（动量、波动率、技术指标、基本面等）
作者：WJC
日期：2026.1.12
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, List
import warnings
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.data.market_data import MarketDataManager
from src.data.financial_data import FinancialDataManager
from src.analysis.technical import TechnicalIndicators

warnings.filterwarnings('ignore')


class FactorCalculator:
    """多因子计算器：计算47个量化因子"""
    
    # 47个因子列表（与聚宽策略一致）
    FACTOR_LIST = [
        'momentum', 'beta', 'sharpe_ratio_60', 'Variance120', 'natural_log_of_market_cap',
        'boll_down', 'Rank1M', 'Variance20', 'MAWVAD', 'single_day_VPT_12', 'ARBR', 
        'cube_of_size', 'intangible_asset_ratio', 'Kurtosis120', 'DAVOL10', 'VR', 
        'sharpe_ratio_20', 'BBIC', 'operating_profit_to_total_profit', 'single_day_VPT', 
        'Volume1M', 'ATR6', 'book_to_price_ratio', 'Skewness20', 'VMACD', 'AR', 
        'Skewness120', 'VOL120', 'cash_flow_to_price_ratio', 'roa_ttm', 
        'arron_down_25', 'price_no_fq', 'net_operate_cash_flow_to_total_liability', 
        'Skewness60', 'TVMA6', 'Kurtosis60', 'non_recurring_gain_loss', 'MASS', 
        'earnings_yield', 'surplus_reserve_fund_per_share', 'earnings_to_price_ratio', 
        'growth', 'MFI14', 'Kurtosis20', 'net_operating_cash_flow_coverage', 'VOSC', 
        'VOL10', 'cash_earnings_to_price_ratio', 'total_operating_revenue_per_share', 
        'sales_to_price_ratio'
    ]
    
    def __init__(self):
        """初始化因子计算器"""
        self.market_data_manager = MarketDataManager()
        self.financial_data_manager = FinancialDataManager()
        self.technical_calculator = TechnicalIndicators()
        
    def calculate_all_factors(self, stock_code: str, end_date: str = None, 
                             lookback_days: int = 250) -> Dict[str, float]:
        """
        计算所有47个因子
        
        Args:
            stock_code: 股票代码
            end_date: 截止日期，格式 'YYYYMMDD'，None表示使用当前日期
            lookback_days: 回看天数（用于计算历史指标）
            
        Returns:
            Dict: 因子值字典，key为因子名，value为因子值
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        # 获取历史数据
        start_date = (datetime.strptime(end_date, '%Y%m%d') - timedelta(days=lookback_days + 60)).strftime('%Y%m%d')
        data = self.market_data_manager.get_local_data(stock_code, '1d', start_date, end_date)
        
        if data is None or data.empty or len(data) < 120:
            # 如果数据不足，返回NaN
            return {factor: np.nan for factor in self.FACTOR_LIST}
        
        # 获取财务数据
        financial_data = self.financial_data_manager.get_financial_data(stock_code, auto_download=False)
        
        # 获取市场数据（用于Beta等计算）
        market_data = self._get_market_index_data(end_date, lookback_days)
        
        factors = {}
        
        # 计算所有因子
        for factor_name in self.FACTOR_LIST:
            try:
                factor_value = self._calculate_single_factor(factor_name, data, financial_data, market_data, end_date)
                factors[factor_name] = factor_value if not pd.isna(factor_value) else 0.0
            except Exception as e:
                # 如果计算失败，使用0.0作为默认值
                factors[factor_name] = 0.0
                # print(f"[警告] 计算因子 {factor_name} 失败: {e}")
        
        return factors
    
    def _calculate_single_factor(self, factor_name: str, data: pd.DataFrame,
                                 financial_data: Optional[Dict], market_data: Optional[pd.DataFrame],
                                 end_date: str) -> float:
        """计算单个因子"""
        if factor_name == 'momentum':
            return self._calculate_momentum(data, period=5)
        elif factor_name == 'beta':
            return self._calculate_beta(data, market_data)
        elif factor_name == 'sharpe_ratio_60':
            return self._calculate_sharpe_ratio(data, period=60)
        elif factor_name == 'sharpe_ratio_20':
            return self._calculate_sharpe_ratio(data, period=20)
        elif factor_name == 'Variance120':
            return self._calculate_variance(data, period=120)
        elif factor_name == 'Variance20':
            return self._calculate_variance(data, period=20)
        elif factor_name == 'natural_log_of_market_cap':
            return self._calculate_log_market_cap(data, financial_data)
        elif factor_name == 'cube_of_size':
            return self._calculate_cube_size(data, financial_data)
        elif factor_name == 'boll_down':
            return self._calculate_boll_down(data)
        elif factor_name == 'Rank1M':
            return self._calculate_rank1m(data)
        elif factor_name == 'MAWVAD':
            return self._calculate_mawvad(data)
        elif factor_name == 'single_day_VPT_12':
            return self._calculate_vpt(data, period=12, single_day=True)
        elif factor_name == 'single_day_VPT':
            return self._calculate_vpt(data, period=1, single_day=True)
        elif factor_name == 'ARBR':
            return self._calculate_arbr(data)
        elif factor_name == 'intangible_asset_ratio':
            return self._calculate_intangible_asset_ratio(financial_data)
        elif factor_name == 'Kurtosis120':
            return self._calculate_kurtosis(data, period=120)
        elif factor_name == 'Kurtosis60':
            return self._calculate_kurtosis(data, period=60)
        elif factor_name == 'Kurtosis20':
            return self._calculate_kurtosis(data, period=20)
        elif factor_name == 'Skewness120':
            return self._calculate_skewness(data, period=120)
        elif factor_name == 'Skewness60':
            return self._calculate_skewness(data, period=60)
        elif factor_name == 'Skewness20':
            return self._calculate_skewness(data, period=20)
        elif factor_name == 'DAVOL10':
            return self._calculate_davol(data, period=10)
        elif factor_name == 'VR':
            return self._calculate_vr(data)
        elif factor_name == 'BBIC':
            return self._calculate_bbic(data)
        elif factor_name == 'operating_profit_to_total_profit':
            return self._calculate_operating_profit_ratio(financial_data)
        elif factor_name == 'Volume1M':
            return self._calculate_volume1m(data)
        elif factor_name == 'ATR6':
            return self._calculate_atr(data, period=6)
        elif factor_name == 'book_to_price_ratio':
            return self._calculate_book_to_price(financial_data, data)
        elif factor_name == 'VMACD':
            return self._calculate_vmacd(data)
        elif factor_name == 'AR':
            return self._calculate_ar(data)
        elif factor_name == 'VOL120':
            return self._calculate_volatility(data, period=120)
        elif factor_name == 'VOL10':
            return self._calculate_volatility(data, period=10)
        elif factor_name == 'cash_flow_to_price_ratio':
            return self._calculate_cash_flow_to_price(financial_data, data)
        elif factor_name == 'cash_earnings_to_price_ratio':
            return self._calculate_cash_earnings_to_price(financial_data, data)
        elif factor_name == 'roa_ttm':
            return self._calculate_roa(financial_data)
        elif factor_name == 'arron_down_25':
            return self._calculate_arron(data, period=25)
        elif factor_name == 'price_no_fq':
            return self._calculate_price_no_fq(data)
        elif factor_name == 'net_operate_cash_flow_to_total_liability':
            return self._calculate_cash_flow_coverage(financial_data)
        elif factor_name == 'net_operating_cash_flow_coverage':
            return self._calculate_net_operating_cash_flow_coverage(financial_data)
        elif factor_name == 'TVMA6':
            return self._calculate_tvma(data, period=6)
        elif factor_name == 'non_recurring_gain_loss':
            return self._calculate_non_recurring_gain_loss(financial_data)
        elif factor_name == 'MASS':
            return self._calculate_mass(data)
        elif factor_name == 'earnings_yield':
            return self._calculate_earnings_yield(financial_data, data)
        elif factor_name == 'earnings_to_price_ratio':
            return self._calculate_earnings_to_price(financial_data, data)
        elif factor_name == 'surplus_reserve_fund_per_share':
            return self._calculate_surplus_reserve_per_share(financial_data)
        elif factor_name == 'growth':
            return self._calculate_growth(financial_data)
        elif factor_name == 'MFI14':
            return self._calculate_mfi(data, period=14)
        elif factor_name == 'VOSC':
            return self._calculate_vosc(data)
        elif factor_name == 'total_operating_revenue_per_share':
            return self._calculate_revenue_per_share(financial_data)
        elif factor_name == 'sales_to_price_ratio':
            return self._calculate_sales_to_price(financial_data, data)
        else:
            return 0.0
    
    # ========== 动量因子 ==========
    
    def _calculate_momentum(self, data: pd.DataFrame, period: int = 5) -> float:
        """计算动量因子（价格变化率）"""
        if len(data) < period + 1:
            return 0.0
        return (data['close'].iloc[-1] / data['close'].iloc[-period-1] - 1) * 100
    
    def _calculate_rank1m(self, data: pd.DataFrame) -> float:
        """计算1月收益率排名"""
        if len(data) < 20:
            return 0.0
        return_1m = (data['close'].iloc[-1] / data['close'].iloc[-20] - 1) * 100
        return return_1m
    
    def _calculate_beta(self, data: pd.DataFrame, market_data: Optional[pd.DataFrame], period: int = 60) -> float:
        """计算Beta（相对市场）"""
        if market_data is None or len(data) < period:
            return 1.0
        
        min_len = min(len(data), len(market_data), period)
        stock_returns = data['close'].pct_change().iloc[-min_len:]
        market_returns = market_data['close'].pct_change().iloc[-min_len:]
        
        cov = np.cov(stock_returns.dropna(), market_returns.dropna())[0, 1]
        market_var = market_returns.var()
        
        if market_var == 0:
            return 1.0
        return cov / market_var
    
    def _calculate_sharpe_ratio(self, data: pd.DataFrame, period: int, risk_free_rate: float = 0.03) -> float:
        """计算夏普比率"""
        if len(data) < period:
            return 0.0
        
        returns = data['close'].pct_change().iloc[-period:].dropna()
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        annual_return = returns.mean() * 252
        annual_vol = returns.std() * np.sqrt(252)
        sharpe = (annual_return - risk_free_rate) / annual_vol if annual_vol > 0 else 0.0
        return sharpe * 100  # 转换为百分比形式
    
    # ========== 波动率因子 ==========
    
    def _calculate_variance(self, data: pd.DataFrame, period: int) -> float:
        """计算波动率（收益率方差）"""
        if len(data) < period:
            return 0.0
        returns = data['close'].pct_change().iloc[-period:].dropna()
        return returns.var() * 10000  # 放大10000倍
    
    def _calculate_volatility(self, data: pd.DataFrame, period: int) -> float:
        """计算波动率（标准差）"""
        if len(data) < period:
            return 0.0
        returns = data['close'].pct_change().iloc[-period:].dropna()
        return returns.std() * 100  # 转换为百分比
    
    def _calculate_kurtosis(self, data: pd.DataFrame, period: int) -> float:
        """计算峰度"""
        if len(data) < period:
            return 0.0
        returns = data['close'].pct_change().iloc[-period:].dropna()
        if len(returns) < 4:
            return 0.0
        return float(returns.kurtosis())
    
    def _calculate_skewness(self, data: pd.DataFrame, period: int) -> float:
        """计算偏度"""
        if len(data) < period:
            return 0.0
        returns = data['close'].pct_change().iloc[-period:].dropna()
        if len(returns) < 3:
            return 0.0
        return float(returns.skew())
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 6) -> float:
        """计算平均真实波幅（ATR）"""
        if len(data) < period + 1:
            return 0.0
        
        high = data['high'].iloc[-period:]
        low = data['low'].iloc[-period:]
        close = data['close'].iloc[-period-1:-1]
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.mean()
        return float(atr) if not pd.isna(atr) else 0.0
    
    # ========== 技术指标因子 ==========
    
    def _calculate_boll_down(self, data: pd.DataFrame, period: int = 20, std_dev: int = 2) -> float:
        """计算布林带下轨"""
        if len(data) < period:
            return 0.0
        ma = data['close'].rolling(window=period).mean().iloc[-1]
        std = data['close'].rolling(window=period).std().iloc[-1]
        boll_down = ma - std_dev * std
        return float(boll_down) if not pd.isna(boll_down) else 0.0
    
    def _calculate_arbr(self, data: pd.DataFrame, period: int = 26) -> float:
        """计算ARBR指标（AR/BR比率）"""
        if len(data) < period:
            return 0.0
        
        high = data['high'].iloc[-period:]
        low = data['low'].iloc[-period:]
        open_price = data['open'].iloc[-period:]
        close = data['close'].iloc[-period-1:-1]
        
        ar = (high - open_price).sum() / (open_price - low).sum() if (open_price - low).sum() != 0 else 1.0
        br = (high - close.shift(1)).sum() / (close.shift(1) - low).sum() if (close.shift(1) - low).sum() != 0 else 1.0
        
        return float(ar / br) if br != 0 else 1.0
    
    def _calculate_ar(self, data: pd.DataFrame, period: int = 26) -> float:
        """计算AR指标"""
        if len(data) < period:
            return 0.0
        
        high = data['high'].iloc[-period:]
        low = data['low'].iloc[-period:]
        open_price = data['open'].iloc[-period:]
        
        ar = (high - open_price).sum() / (open_price - low).sum() if (open_price - low).sum() != 0 else 100.0
        return float(ar) * 100
    
    def _calculate_vr(self, data: pd.DataFrame, period: int = 26) -> float:
        """计算VR指标（成交量比率）"""
        if len(data) < period:
            return 0.0
        
        close = data['close'].iloc[-period:]
        prev_close = data['close'].iloc[-period-1:-1]
        volume = data['volume'].iloc[-period:]
        
        up_volume = volume[close > prev_close.shift(1)].sum()
        down_volume = volume[close < prev_close.shift(1)].sum()
        flat_volume = volume[close == prev_close.shift(1)].sum()
        
        vr = (up_volume + flat_volume / 2) / (down_volume + flat_volume / 2) if (down_volume + flat_volume / 2) != 0 else 1.0
        return float(vr) * 100
    
    def _calculate_mfi(self, data: pd.DataFrame, period: int = 14) -> float:
        """计算MFI（资金流量指标）"""
        if len(data) < period + 1:
            return 50.0
        
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        money_flow = typical_price * data['volume']
        
        positive_flow = money_flow.iloc[-period:][typical_price.iloc[-period:] > typical_price.iloc[-period-1:-1].shift(1)].sum()
        negative_flow = money_flow.iloc[-period:][typical_price.iloc[-period:] < typical_price.iloc[-period-1:-1].shift(1)].sum()
        
        if negative_flow == 0:
            return 100.0
        mfi = 100 - (100 / (1 + positive_flow / negative_flow))
        return float(mfi)
    
    def _calculate_vmacd(self, data: pd.DataFrame, fast: int = 12, slow: int = 26) -> float:
        """计算成交量MACD"""
        if len(data) < slow:
            return 0.0
        
        volume = data['volume'].iloc[-slow:]
        ema_fast = volume.ewm(span=fast, adjust=False).mean().iloc[-1]
        ema_slow = volume.ewm(span=slow, adjust=False).mean().iloc[-1]
        vmacd = ema_fast - ema_slow
        return float(vmacd)
    
    def _calculate_vosc(self, data: pd.DataFrame, short: int = 12, long: int = 26) -> float:
        """计算成交量振荡器"""
        if len(data) < long:
            return 0.0
        
        volume = data['volume'].iloc[-long:]
        ma_short = volume.rolling(window=short).mean().iloc[-1]
        ma_long = volume.rolling(window=long).mean().iloc[-1]
        
        vosc = (ma_short - ma_long) / ma_long * 100 if ma_long != 0 else 0.0
        return float(vosc)
    
    def _calculate_bbic(self, data: pd.DataFrame, period: int = 20) -> float:
        """计算BBIC指标（布林带宽度）"""
        if len(data) < period:
            return 0.0
        
        ma = data['close'].rolling(window=period).mean().iloc[-1]
        std = data['close'].rolling(window=period).std().iloc[-1]
        current_price = data['close'].iloc[-1]
        
        bbic = (current_price - ma) / std if std != 0 else 0.0
        return float(bbic)
    
    def _calculate_arron(self, data: pd.DataFrame, period: int = 25) -> float:
        """计算ARRON指标（向下）"""
        if len(data) < period:
            return 0.0
        
        high = data['high'].iloc[-period:]
        highest_idx = high.idxmax()
        days_since_high = len(data) - 1 - data.index.get_loc(highest_idx)
        
        arron_down = (period - days_since_high) / period * 100
        return float(arron_down)
    
    def _calculate_mass(self, data: pd.DataFrame, period: int = 9) -> float:
        """计算MASS指标"""
        if len(data) < period * 2:
            return 0.0
        
        ema1 = data['close'].ewm(span=period).mean()
        ema2 = ema1.ewm(span=period).mean()
        
        diff = ema1 - ema2
        mass = diff.rolling(window=period).sum().iloc[-1]
        return float(mass) if not pd.isna(mass) else 0.0
    
    # ========== 成交量因子 ==========
    
    def _calculate_volume1m(self, data: pd.DataFrame) -> float:
        """计算1月平均成交量"""
        if len(data) < 20:
            return 0.0
        avg_volume = data['volume'].iloc[-20:].mean()
        return float(avg_volume)
    
    def _calculate_davol(self, data: pd.DataFrame, period: int = 10) -> float:
        """计算成交量比率（DAVOL）"""
        if len(data) < period:
            return 1.0
        
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].iloc[-period:].mean()
        davol = current_volume / avg_volume if avg_volume != 0 else 1.0
        return float(davol)
    
    def _calculate_mawvad(self, data: pd.DataFrame, period: int = 6) -> float:
        """计算成交量加权移动平均"""
        if len(data) < period:
            return 0.0
        
        close = data['close'].iloc[-period:]
        volume = data['volume'].iloc[-period:]
        
        vwap = (close * volume).sum() / volume.sum() if volume.sum() != 0 else close.mean()
        return float(vwap)
    
    def _calculate_tvma(self, data: pd.DataFrame, period: int = 6) -> float:
        """计算成交量移动平均"""
        if len(data) < period:
            return 0.0
        tvma = data['volume'].rolling(window=period).mean().iloc[-1]
        return float(tvma) if not pd.isna(tvma) else 0.0
    
    def _calculate_vpt(self, data: pd.DataFrame, period: int = 12, single_day: bool = False) -> float:
        """计算价量趋势（VPT）"""
        if len(data) < period + 1:
            return 0.0
        
        close = data['close'].iloc[-period:]
        prev_close = data['close'].iloc[-period-1:-1]
        volume = data['volume'].iloc[-period:]
        
        price_change = (close - prev_close.shift(1)) / prev_close.shift(1)
        vpt = (price_change * volume).sum()
        
        if single_day:
            return float(vpt.iloc[-1]) if len(vpt) > 0 else 0.0
        else:
            return float(vpt.sum())
    
    # ========== 基本面因子 ==========
    
    def _calculate_log_market_cap(self, data: pd.DataFrame, financial_data: Optional[Dict]) -> float:
        """计算市值对数"""
        if financial_data is None:
            return 0.0
        market_cap = financial_data.get('market_cap', 0)
        if market_cap and market_cap > 0:
            return float(np.log(market_cap))
        return 0.0
    
    def _calculate_cube_size(self, data: pd.DataFrame, financial_data: Optional[Dict]) -> float:
        """计算市值立方"""
        if financial_data is None:
            return 0.0
        market_cap = financial_data.get('market_cap', 0)
        if market_cap and market_cap > 0:
            return float((market_cap / 1e8) ** 3)  # 转换为亿元后立方
        return 0.0
    
    def _calculate_book_to_price(self, financial_data: Optional[Dict], data: pd.DataFrame) -> float:
        """计算市净率（PB的倒数）"""
        if financial_data is None:
            return 0.0
        pb = financial_data.get('pb', None)
        if pb and pb > 0:
            return float(1.0 / pb)
        return 0.0
    
    def _calculate_earnings_yield(self, financial_data: Optional[Dict], data: pd.DataFrame) -> float:
        """计算盈利收益率（PE的倒数）"""
        if financial_data is None:
            return 0.0
        pe = financial_data.get('pe', None)
        if pe and pe > 0:
            return float(1.0 / pe * 100)  # 转换为百分比
        return 0.0
    
    def _calculate_earnings_to_price(self, financial_data: Optional[Dict], data: pd.DataFrame) -> float:
        """计算盈利价格比（EPS/Price）"""
        if financial_data is None or data.empty:
            return 0.0
        eps = financial_data.get('eps', None)
        current_price = data['close'].iloc[-1]
        if eps and current_price > 0:
            return float(eps / current_price)
        return 0.0
    
    def _calculate_cash_flow_to_price(self, financial_data: Optional[Dict], data: pd.DataFrame) -> float:
        """计算现金流价格比"""
        if financial_data is None or data.empty:
            return 0.0
        cash_flow = financial_data.get('operating_cash_flow', None)
        market_cap = financial_data.get('market_cap', None)
        if cash_flow and market_cap and market_cap > 0:
            return float(cash_flow / market_cap)
        return 0.0
    
    def _calculate_cash_earnings_to_price(self, financial_data: Optional[Dict], data: pd.DataFrame) -> float:
        """计算现金盈利价格比"""
        if financial_data is None or data.empty:
            return 0.0
        cash_earnings = financial_data.get('operating_cash_flow', None)
        market_cap = financial_data.get('market_cap', None)
        if cash_earnings and market_cap and market_cap > 0:
            return float(cash_earnings / market_cap)
        return 0.0
    
    def _calculate_sales_to_price(self, financial_data: Optional[Dict], data: pd.DataFrame) -> float:
        """计算市销率（PS的倒数）"""
        if financial_data is None or data.empty:
            return 0.0
        revenue = financial_data.get('operating_revenue', None)
        market_cap = financial_data.get('market_cap', None)
        if revenue and market_cap and market_cap > 0:
            return float(revenue / market_cap)
        return 0.0
    
    def _calculate_roa(self, financial_data: Optional[Dict]) -> float:
        """计算ROA（总资产收益率）"""
        if financial_data is None:
            return 0.0
        roa = financial_data.get('roa', None)
        if roa is not None:
            return float(roa * 100)  # 转换为百分比
        return 0.0
    
    def _calculate_intangible_asset_ratio(self, financial_data: Optional[Dict]) -> float:
        """计算无形资产比率"""
        if financial_data is None:
            return 0.0
        intangible_assets = financial_data.get('intangible_assets', 0)
        total_assets = financial_data.get('total_assets', 0)
        if total_assets and total_assets > 0:
            return float(intangible_assets / total_assets)
        return 0.0
    
    def _calculate_operating_profit_ratio(self, financial_data: Optional[Dict]) -> float:
        """计算营业利润占比"""
        if financial_data is None:
            return 0.0
        operating_profit = financial_data.get('operating_profit', 0)
        total_profit = financial_data.get('total_profit', 0)
        if total_profit and total_profit != 0:
            return float(operating_profit / total_profit)
        return 0.0
    
    def _calculate_cash_flow_coverage(self, financial_data: Optional[Dict]) -> float:
        """计算现金流覆盖率"""
        if financial_data is None:
            return 0.0
        operating_cash_flow = financial_data.get('operating_cash_flow', 0)
        total_liability = financial_data.get('total_liability', 0)
        if total_liability and total_liability > 0:
            return float(operating_cash_flow / total_liability)
        return 0.0
    
    def _calculate_net_operating_cash_flow_coverage(self, financial_data: Optional[Dict]) -> float:
        """计算净经营现金流覆盖率"""
        if financial_data is None:
            return 0.0
        net_operating_cash_flow = financial_data.get('net_operating_cash_flow', 0)
        total_liability = financial_data.get('total_liability', 0)
        if total_liability and total_liability > 0:
            return float(net_operating_cash_flow / total_liability)
        return 0.0
    
    def _calculate_non_recurring_gain_loss(self, financial_data: Optional[Dict]) -> float:
        """计算非经常性损益"""
        if financial_data is None:
            return 0.0
        non_recurring = financial_data.get('non_recurring_profit', 0)
        return float(non_recurring)
    
    def _calculate_surplus_reserve_per_share(self, financial_data: Optional[Dict]) -> float:
        """计算每股盈余公积"""
        if financial_data is None:
            return 0.0
        surplus_reserve = financial_data.get('surplus_reserve', 0)
        total_shares = financial_data.get('total_shares', 0)
        if total_shares and total_shares > 0:
            return float(surplus_reserve / total_shares)
        return 0.0
    
    def _calculate_revenue_per_share(self, financial_data: Optional[Dict]) -> float:
        """计算每股营业收入"""
        if financial_data is None:
            return 0.0
        operating_revenue = financial_data.get('operating_revenue', 0)
        total_shares = financial_data.get('total_shares', 0)
        if total_shares and total_shares > 0:
            return float(operating_revenue / total_shares)
        return 0.0
    
    def _calculate_growth(self, financial_data: Optional[Dict]) -> float:
        """计算成长性（净利润增长率）"""
        if financial_data is None:
            return 0.0
        profit_growth = financial_data.get('profit_growth', 0)
        return float(profit_growth)
    
    def _calculate_price_no_fq(self, data: pd.DataFrame) -> float:
        """计算未复权价格"""
        # XTquant获取的数据默认是前复权，这里返回当前价格
        if data.empty:
            return 0.0
        return float(data['close'].iloc[-1])
    
    # ========== 辅助方法 ==========
    
    def _get_market_index_data(self, end_date: str, lookback_days: int) -> Optional[pd.DataFrame]:
        """获取市场指数数据（用于Beta计算）"""
        try:
            start_date = (datetime.strptime(end_date, '%Y%m%d') - timedelta(days=lookback_days + 30)).strftime('%Y%m%d')
            # 使用沪深300指数 '000300.SH' 作为市场基准
            market_data = self.market_data_manager.get_local_data('000300.SH', '1d', start_date, end_date)
            return market_data
        except:
            return None
    
    def batch_calculate_factors(self, stock_list: List[str], end_date: str = None) -> pd.DataFrame:
        """
        批量计算多个股票的因子
        
        Args:
            stock_list: 股票代码列表
            end_date: 截止日期
            
        Returns:
            DataFrame: 因子值DataFrame，行为股票代码，列为因子名
        """
        results = {}
        for stock_code in stock_list:
            factors = self.calculate_all_factors(stock_code, end_date)
            results[stock_code] = factors
        
        return pd.DataFrame(results).T
