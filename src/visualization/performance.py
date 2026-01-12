# performance.py
"""
回测性能可视化模块
功能：绘制回测结果的性能图表
作者：WJC
日期：2026.1.5
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Tuple
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.strategy.strategies import Signal


class PerformancePlotter:
    """回测性能图表绘制器"""
    
    def __init__(self):
        """初始化性能图表绘制器"""
        pass
    
    def plot_performance(self, backtest_result: pd.DataFrame, symbol: str) -> Tuple[plt.Figure, list]:
        """
        绘制回测结果图表
        
        Args:
            backtest_result: 回测结果DataFrame
            symbol: 股票代码
            
        Returns:
            Tuple: (figure, axes)
        """
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        
        # 1. 价格和信号
        ax1 = axes[0]
        ax1.plot(backtest_result.index, backtest_result['close'], 
                label='Price', color='black', linewidth=1.5)
        
        buy_signals = backtest_result[backtest_result['signal'] == Signal.BUY.value]
        sell_signals = backtest_result[backtest_result['signal'] == Signal.SELL.value]
        
        ax1.scatter(buy_signals.index, buy_signals['close'], 
                   color='red', marker='^', s=100, label='Buy', zorder=5)
        ax1.scatter(sell_signals.index, sell_signals['close'], 
                   color='green', marker='v', s=100, label='Sell', zorder=5)
        
        ax1.set_title(f'{symbol} - Trading Signals', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 权益曲线
        ax2 = axes[1]
        ax2.plot(backtest_result.index, backtest_result['equity'], 
                label='Strategy Equity', color='blue', linewidth=2)
        ax2.plot(backtest_result.index, 
                backtest_result['close'] / backtest_result['close'].iloc[0] * backtest_result['equity'].iloc[0],
                label='Buy & Hold', color='gray', linestyle='--', linewidth=1.5)
        ax2.set_title('Equity Curve', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Equity', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 累计收益率
        ax3 = axes[2]
        ax3.plot(backtest_result.index, backtest_result['cumulative_returns'] * 100, 
                label='Strategy Returns', color='blue', linewidth=2)
        ax3.plot(backtest_result.index, backtest_result['benchmark_cumulative'] * 100, 
                label='Benchmark Returns', color='gray', linestyle='--', linewidth=1.5)
        ax3.set_title('Cumulative Returns', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Returns (%)', fontsize=12)
        ax3.set_xlabel('Date', fontsize=12)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 格式化x轴日期
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        return fig, axes
