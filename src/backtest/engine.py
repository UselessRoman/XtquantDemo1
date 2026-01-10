# engine.py
"""
回测引擎模块
功能：策略回测执行
"""

import numpy as np
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.config import BacktestConfig
from src.strategy.strategies import Signal


class BacktestEngine:
    """策略回测引擎"""
    
    def __init__(self, initial_capital: float = None, 
                 commission_rate: float = None,
                 slippage_rate: float = None):
        """
        Args:
            initial_capital: 初始资金
            commission_rate: 手续费率
            slippage_rate: 滑点率
        """
        self.initial_capital = initial_capital or BacktestConfig.INITIAL_CAPITAL
        self.commission_rate = commission_rate or BacktestConfig.COMMISSION_RATE
        self.slippage_rate = slippage_rate or BacktestConfig.SLIPPAGE_RATE
        self.trades = None
    
    def run(self, data: pd.DataFrame, signals: pd.Series) -> pd.DataFrame:
        """
        执行回测
        
        Args:
            data: 股票数据
            signals: 交易信号序列
            
        Returns:
            DataFrame: 回测结果
        """
        # 初始化
        capital = self.initial_capital
        position = 0  # 持仓数量
        cash = capital  # 现金
        
        # 记录每笔交易
        trades = []
        positions = []  # 每日持仓
        equity = []  # 每日权益
        
        for i in range(len(data)):
            current_price = data['close'].iloc[i]
            signal = signals.iloc[i]
            
            # 执行交易
            if signal == Signal.BUY.value and position == 0:
                # 买入：考虑滑点和手续费
                buy_price = current_price * (1 + self.slippage_rate)
                commission = capital * self.commission_rate
                position = (cash - commission) / buy_price
                cash = 0
                
                trades.append({
                    'date': data.index[i],
                    'action': 'BUY',
                    'price': buy_price,
                    'shares': position,
                    'capital': capital
                })
            
            elif signal == Signal.SELL.value and position > 0:
                # 卖出：考虑滑点和手续费
                sell_price = current_price * (1 - self.slippage_rate)
                cash = position * sell_price * (1 - self.commission_rate)
                position = 0
                
                trades.append({
                    'date': data.index[i],
                    'action': 'SELL',
                    'price': sell_price,
                    'shares': 0,
                    'capital': cash
                })
            
            # 计算当前权益
            if position > 0:
                current_equity = position * current_price
            else:
                current_equity = cash
            
            positions.append(position)
            equity.append(current_equity)
            capital = current_equity
        
        # 构建结果DataFrame
        result = data.copy()
        result['signal'] = signals
        result['position'] = positions
        result['equity'] = equity
        result['returns'] = result['equity'].pct_change()
        result['cumulative_returns'] = (1 + result['returns']).cumprod() - 1
        
        # 计算基准收益（买入持有）
        result['benchmark_returns'] = result['close'].pct_change()
        result['benchmark_cumulative'] = (1 + result['benchmark_returns']).cumprod() - 1
        
        self.trades = pd.DataFrame(trades)
        return result
