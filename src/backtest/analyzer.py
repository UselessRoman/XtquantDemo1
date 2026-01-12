# analyzer.py
"""
性能分析器模块
功能：回测结果性能分析（不包含可视化）
"""

import numpy as np
import pandas as pd
from typing import Dict
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.config import BacktestConfig
from src.strategy.strategies import Signal


class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self, risk_free_rate: float = None):
        """
        Args:
            risk_free_rate: 无风险利率（年化）
        """
        self.risk_free_rate = risk_free_rate or BacktestConfig.RISK_FREE_RATE
    
    def analyze(self, backtest_result: pd.DataFrame) -> Dict:
        """
        分析回测结果
        
        Args:
            backtest_result: 回测结果DataFrame
            
        Returns:
            Dict: 性能指标字典
        """
        equity = backtest_result['equity']
        returns = backtest_result['returns'].dropna()
        
        # 总收益率
        total_return = (equity.iloc[-1] / equity.iloc[0] - 1) * 100
        
        # 年化收益率
        days = len(backtest_result)
        years = days / 252  # 假设252个交易日
        if years > 0:
            annual_return = ((equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1) * 100
        else:
            annual_return = 0
        
        # 波动率（年化）
        volatility = returns.std() * np.sqrt(252) * 100
        
        # 夏普比率
        sharpe_ratio = (annual_return - self.risk_free_rate * 100) / volatility if volatility > 0 else 0
        
        # 最大回撤
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative / running_max - 1) * 100
        max_drawdown = drawdown.min()
        
        # 胜率
        trade_returns = []
        in_position = False
        entry_price = 0
        
        for i in range(len(backtest_result)):
            if backtest_result['signal'].iloc[i] == Signal.BUY.value and not in_position:
                in_position = True
                entry_price = backtest_result['close'].iloc[i]
            elif backtest_result['signal'].iloc[i] == Signal.SELL.value and in_position:
                trade_return = (backtest_result['close'].iloc[i] / entry_price - 1) * 100
                trade_returns.append(trade_return)
                in_position = False
        
        win_rate = (sum(1 for r in trade_returns if r > 0) / len(trade_returns) * 100 
                   if trade_returns else 0)
        
        # 基准对比
        benchmark_total = backtest_result['benchmark_cumulative'].iloc[-1] * 100
        
        # 计算最大回撤期间
        max_dd_idx = drawdown.idxmin()
        max_dd_start = cumulative[:max_dd_idx].idxmax() if max_dd_idx is not None else None
        
        return {
            '总收益率': f"{total_return:.2f}%",
            '年化收益率': f"{annual_return:.2f}%",
            '波动率': f"{volatility:.2f}%",
            '夏普比率': f"{sharpe_ratio:.2f}",
            '最大回撤': f"{max_drawdown:.2f}%",
            '胜率': f"{win_rate:.2f}%",
            '交易次数': str(len(trade_returns)),
            '基准收益率': f"{benchmark_total:.2f}%",
            '超额收益': f"{total_return - benchmark_total:.2f}%",
            '最大回撤开始': max_dd_start.strftime('%Y-%m-%d') if max_dd_start is not None else 'N/A',
            '最大回撤结束': max_dd_idx.strftime('%Y-%m-%d') if max_dd_idx is not None else 'N/A'
        }
