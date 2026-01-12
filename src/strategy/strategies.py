# strategies.py
"""
量化策略模块
功能：定义各种交易策略，生成交易信号
作者：WJC
日期：2026.1.5
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from enum import Enum
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.selection.selector import MLStockSelector


class Signal(Enum):
    """交易信号"""
    BUY = 1      # 买入
    SELL = -1    # 卖出
    HOLD = 0     # 持有


class SignalGenerator:
    """交易信号生成器基类"""
    
    def generate_signals(self, data: pd.DataFrame, indicators: Dict) -> pd.Series:
        """
        生成交易信号
        
        Args:
            data: 股票数据
            indicators: 技术指标字典
            
        Returns:
            Series: 交易信号序列 (1=买入, -1=卖出, 0=持有)
        """
        raise NotImplementedError("子类必须实现此方法")


class MACDStrategy(SignalGenerator):
    """MACD策略：DIF上穿DEA买入，下穿卖出"""
    
    def __init__(self, dif_threshold: float = 0, dea_threshold: float = 0):
        """
        Args:
            dif_threshold: DIF阈值，大于此值才买入
            dea_threshold: DEA阈值
        """
        self.dif_threshold = dif_threshold
        self.dea_threshold = dea_threshold
    
    def generate_signals(self, data: pd.DataFrame, indicators: Dict) -> pd.Series:
        """生成MACD策略信号"""
        macd_data = indicators['macd']
        signals = pd.Series(0, index=data.index, dtype=int)
        
        dif = macd_data['DIF']
        dea = macd_data['DEA']
        macd = macd_data['MACD']
        
        # 计算金叉死叉
        for i in range(1, len(data)):
            # 金叉：DIF上穿DEA 且 MACD>0
            if (dif.iloc[i] > dea.iloc[i] and 
                dif.iloc[i-1] <= dea.iloc[i-1] and
                macd.iloc[i] > self.dif_threshold):
                signals.iloc[i] = Signal.BUY.value
            
            # 死叉：DIF下穿DEA 且 MACD<0
            elif (dif.iloc[i] < dea.iloc[i] and 
                  dif.iloc[i-1] >= dea.iloc[i-1] and
                  macd.iloc[i] < self.dea_threshold):
                signals.iloc[i] = Signal.SELL.value
        
        return signals


class MAStrategy(SignalGenerator):
    """均线策略：价格上穿均线买入，下穿卖出"""
    
    def __init__(self, ma_period: int = 20, use_multiple_ma: bool = False):
        """
        Args:
            ma_period: 均线周期
            use_multiple_ma: 是否使用多均线（MA5上穿MA10买入）
        """
        self.ma_period = ma_period
        self.use_multiple_ma = use_multiple_ma
    
    def generate_signals(self, data: pd.DataFrame, indicators: Dict) -> pd.Series:
        """生成均线策略信号"""
        signals = pd.Series(0, index=data.index, dtype=int)
        ma_data = indicators['ma']
        close = data['close']
        
        if self.use_multiple_ma:
            # 多均线策略：MA5上穿MA10买入
            ma5 = ma_data['MA5']
            ma10 = ma_data['MA10']
            
            for i in range(1, len(data)):
                if (ma5.iloc[i] > ma10.iloc[i] and 
                    ma5.iloc[i-1] <= ma10.iloc[i-1]):
                    signals.iloc[i] = Signal.BUY.value
                elif (ma5.iloc[i] < ma10.iloc[i] and 
                      ma5.iloc[i-1] >= ma10.iloc[i-1]):
                    signals.iloc[i] = Signal.SELL.value
        else:
            # 单均线策略：价格上穿均线买入
            ma = ma_data[f'MA{self.ma_period}']
            
            for i in range(1, len(data)):
                if (close.iloc[i] > ma.iloc[i] and 
                    close.iloc[i-1] <= ma.iloc[i-1]):
                    signals.iloc[i] = Signal.BUY.value
                elif (close.iloc[i] < ma.iloc[i] and 
                      close.iloc[i-1] >= ma.iloc[i-1]):
                    signals.iloc[i] = Signal.SELL.value
        
        return signals


class KDJStrategy(SignalGenerator):
    """KDJ策略：K<20买入，K>80卖出"""
    
    def __init__(self, oversold: float = 20, overbought: float = 80):
        """
        Args:
            oversold: 超卖阈值
            overbought: 超买阈值
        """
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, data: pd.DataFrame, indicators: Dict) -> pd.Series:
        """生成KDJ策略信号"""
        kdj_data = indicators['kdj']
        signals = pd.Series(0, index=data.index, dtype=int)
        
        k = kdj_data['K']
        d = kdj_data['D']
        
        for i in range(1, len(data)):
            # 超卖区域，K上穿D买入
            if (k.iloc[i] < self.oversold and 
                k.iloc[i] > d.iloc[i] and 
                k.iloc[i-1] <= d.iloc[i-1]):
                signals.iloc[i] = Signal.BUY.value
            
            # 超买区域，K下穿D卖出
            elif (k.iloc[i] > self.overbought and 
                  k.iloc[i] < d.iloc[i] and 
                  k.iloc[i-1] >= d.iloc[i-1]):
                signals.iloc[i] = Signal.SELL.value
        
        return signals


class CombinedStrategy(SignalGenerator):
    """组合策略：多个策略信号组合"""
    
    def __init__(self, strategies: List[SignalGenerator], 
                 vote_threshold: int = 2):
        """
        Args:
            strategies: 策略列表
            vote_threshold: 需要多少个策略同时发出信号才执行
        """
        self.strategies = strategies
        self.vote_threshold = vote_threshold
    
    def generate_signals(self, data: pd.DataFrame, indicators: Dict) -> pd.Series:
        """生成组合策略信号"""
        signals = pd.Series(0, index=data.index, dtype=int)
        
        # 获取所有策略的信号
        strategy_signals = []
        for strategy in self.strategies:
            sig = strategy.generate_signals(data, indicators)
            strategy_signals.append(sig)
        
        # 投票机制
        for i in range(len(data)):
            buy_votes = sum(1 for sig in strategy_signals if sig.iloc[i] == Signal.BUY.value)
            sell_votes = sum(1 for sig in strategy_signals if sig.iloc[i] == Signal.SELL.value)
            
            if buy_votes >= self.vote_threshold:
                signals.iloc[i] = Signal.BUY.value
            elif sell_votes >= self.vote_threshold:
                signals.iloc[i] = Signal.SELL.value
        
        return signals


class RSIStrategy(SignalGenerator):
    """RSI策略：RSI<30买入，RSI>70卖出"""
    
    def __init__(self, period: int = 14, oversold: float = 30, overbought: float = 70):
        """
        Args:
            period: RSI计算周期
            oversold: 超卖阈值
            overbought: 超买阈值
        """
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def _calculate_rsi(self, data: pd.DataFrame) -> pd.Series:
        """计算RSI指标"""
        close = data['close']
        delta = close.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        rs = gain / (loss + 1e-8)
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signals(self, data: pd.DataFrame, indicators: Dict) -> pd.Series:
        """生成RSI策略信号"""
        signals = pd.Series(0, index=data.index, dtype=int)
        rsi = self._calculate_rsi(data)
        
        for i in range(1, len(data)):
            # 超卖区域买入
            if rsi.iloc[i] < self.oversold and rsi.iloc[i-1] >= self.oversold:
                signals.iloc[i] = Signal.BUY.value
            # 超买区域卖出
            elif rsi.iloc[i] > self.overbought and rsi.iloc[i-1] <= self.overbought:
                signals.iloc[i] = Signal.SELL.value
        
        return signals


class MLMultiFactorStrategy(SignalGenerator):
    """机器学习多因子策略：基于47因子+ML模型的策略"""
    
    def __init__(self, model_path: str, stock_num: int = 7, score_threshold: float = 0.61,
                 rebalance_freq: str = 'monthly', rebalance_days: List[int] = [1, 15]):
        """
        初始化ML多因子策略
        
        Args:
            model_path: 模型文件路径
            stock_num: 持仓股票数量
            score_threshold: 得分阈值
            rebalance_freq: 调仓频率（'monthly'或'daily'）
            rebalance_days: 调仓日期（每月几号），仅在rebalance_freq='monthly'时有效
        """
        self.selector = MLStockSelector(model_path, stock_num, score_threshold)
        self.stock_num = stock_num
        self.rebalance_freq = rebalance_freq
        self.rebalance_days = rebalance_days
        self.current_holdings = []  # 当前持仓
    
    def generate_signals(self, data: pd.DataFrame, indicators: Dict, 
                        end_date: str = None, context: Dict = None) -> pd.Series:
        """
        生成交易信号（用于回测）
        
        Args:
            data: 股票数据（单个股票）
            indicators: 技术指标（单个股票）
            end_date: 截止日期
            context: 上下文信息（包含选股日期等）
            
        Returns:
            Series: 交易信号序列
        """
        # 注意：ML策略是基于多股票选股的，单个股票的generate_signals不太适用
        # 这里返回持有信号，实际的选股和调仓逻辑应该在回测引擎中处理
        
        signals = pd.Series(Signal.HOLD.value, index=data.index, dtype=int)
        
        # 如果提供了context且有选股结果，则根据持仓状态生成信号
        if context and 'selected_stocks' in context:
            stock_code = context.get('stock_code', '')
            selected_stocks = context.get('selected_stocks', [])
            
            # 如果当前日期是调仓日
            if context.get('is_rebalance_day', False):
                if stock_code in selected_stocks:
                    # 买入信号（如果未持仓）
                    if stock_code not in self.current_holdings:
                        signals.iloc[-1] = Signal.BUY.value
                        self.current_holdings.append(stock_code)
                else:
                    # 卖出信号（如果已持仓）
                    if stock_code in self.current_holdings:
                        signals.iloc[-1] = Signal.SELL.value
                        if stock_code in self.current_holdings:
                            self.current_holdings.remove(stock_code)
        
        return signals
    
    def select_stocks_for_backtest(self, end_date: str = None) -> Tuple[List[str], List[float]]:
        """
        为回测选择股票（调用ML选股器）
        
        Args:
            end_date: 截止日期
            
        Returns:
            Tuple[List[str], List[float]]: (选中的股票列表, 对应的模型得分)
        """
        return self.selector.select_stocks_ml(end_date)
    
    def update_holdings(self, holdings: List[str]):
        """更新当前持仓"""
        self.current_holdings = holdings
