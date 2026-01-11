# main.py
"""
量化交易框架主程序
功能：整合数据管理、分析、策略、回测等功能
作者：WJC
日期：2026.1.5
"""

import sys
import os

# 添加项目根目录到路径（确保可以导入 src.* 模块）
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.data.market_data import MarketDataManager
from src.analysis.technical import TechnicalIndicators, ChartPlotter
from src.strategy.strategies import MACDStrategy, MAStrategy, KDJStrategy, CombinedStrategy
from src.backtest.engine import BacktestEngine
from src.backtest.analyzer import PerformanceAnalyzer
from src.trading.trader import Trader
from src.trading.auto_trader import AutoTrader
from src.selection.selector import StockSelector
from src.core.config import ChartConfig, BacktestConfig
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict


class QuantFramework:
    """量化交易框架主类"""
    
    def __init__(self, enable_trading: bool = False, 
                 qmt_path: str = None, account_id: str = None):
        """
        初始化框架
        
        Args:
            enable_trading: 是否启用交易功能
            qmt_path: QMT客户端路径（交易功能启用时）
            account_id: 资金账号（交易功能启用时）
        """
        self.data_manager = MarketDataManager()
        self.indicator_calculator = TechnicalIndicators()
        self.chart_plotter = ChartPlotter()
        self.backtest_engine = BacktestEngine()
        self.performance_analyzer = PerformanceAnalyzer()
        
        # 交易相关
        self.enable_trading = enable_trading
        self.trader = None
        self.auto_trader = None
        
        # 选股相关
        self.stock_selector = StockSelector()
        
        if enable_trading:
            self.trader = Trader(qmt_path=qmt_path, account_id=account_id)
            self.auto_trader = AutoTrader(trader=self.trader)
    
    def download_data(self, stock_id: str, period: str = "1d",
                     start_time: str = None, end_time: str = None) -> bool:
        """
        下载历史数据
        
        Args:
            stock_id: 股票代码
            period: 周期
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            bool: 是否成功
        """
        return self.data_manager.download_history_data(
            stock_id, period, start_time, end_time
        )
    
    def update_data(self, stock_id: str, period: str = "1d") -> bool:
        """
        更新数据
        
        Args:
            stock_id: 股票代码
            period: 周期
            
        Returns:
            bool: 是否成功
        """
        return self.data_manager.update_data(stock_id, period)
    
    def get_data(self, stock_id: str, period: str = "1d",
                start_time: str = None, end_time: str = None):
        """
        获取本地数据
        
        Args:
            stock_id: 股票代码
            period: 周期
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            DataFrame: 股票数据
        """
        return self.data_manager.get_local_data(
            stock_id, period, start_time, end_time
        )
    
    def analyze_data(self, stock_id: str, period: str = "1d",
                    start_time: str = None, end_time: str = None,
                    save_chart: bool = True):
        """
        分析数据并绘制图表
        
        Args:
            stock_id: 股票代码
            period: 周期
            start_time: 开始时间
            end_time: 结束时间
            save_chart: 是否保存图表
        """
        print(f"\n{'=' * 60}")
        print(f"分析股票: {stock_id}")
        print(f"{'=' * 60}")
        
        # 获取数据
        data = self.get_data(stock_id, period, start_time, end_time)
        if data is None or data.empty:
            print("[错误] 无法获取数据")
            return
        
        # 计算技术指标
        print("计算技术指标...")
        indicators = self.indicator_calculator.calculate_all(data)
        
        # 绘制图表
        print("绘制图表...")
        fig, axes = self.chart_plotter.create_chart(data, indicators, stock_id)
        
        # 保存图表
        if save_chart:
            save_path = f"{stock_id.replace('.', '_')}_analysis.png"
            plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
            print(f"[成功] 图表已保存: {save_path}")
        
        plt.show()
        
        # 显示统计信息
        self._display_statistics(data, stock_id)
    
    def run_backtest(self, stock_id: str, strategy, period: str = "1d",
                    start_time: str = None, end_time: str = None,
                    save_chart: bool = True):
        """
        运行策略回测
        
        Args:
            stock_id: 股票代码
            strategy: 交易策略对象
            period: 周期
            start_time: 开始时间
            end_time: 结束时间
            save_chart: 是否保存图表
            
        Returns:
            Dict: 回测结果
        """
        print(f"\n{'=' * 60}")
        print(f"运行策略回测: {stock_id}")
        print(f"策略: {strategy.__class__.__name__}")
        print(f"{'=' * 60}")
        
        # 获取数据
        data = self.get_data(stock_id, period, start_time, end_time)
        if data is None or data.empty:
            print("[错误] 无法获取数据")
            return None
        
        # 计算技术指标
        print("计算技术指标...")
        indicators = self.indicator_calculator.calculate_all(data)
        
        # 生成交易信号
        print("生成交易信号...")
        signals = strategy.generate_signals(data, indicators)
        signal_count = signals.value_counts()
        print(f"买入信号: {signal_count.get(1, 0)} 次")
        print(f"卖出信号: {signal_count.get(-1, 0)} 次")
        
        # 执行回测
        print("执行回测...")
        backtest_result = self.backtest_engine.run(data, signals)
        
        # 性能分析
        print("分析性能...")
        performance = self.performance_analyzer.analyze(backtest_result)
        
        # 显示结果
        print(f"\n{'=' * 60}")
        print("回测结果")
        print(f"{'=' * 60}")
        for key, value in performance.items():
            print(f"{key:>12}: {value}")
        
        # 绘制图表
        print("\n绘制回测图表...")
        fig, axes = self.performance_analyzer.plot_performance(backtest_result, stock_id)
        
        # 保存图表
        if save_chart:
            save_path = f"{stock_id.replace('.', '_')}_backtest.png"
            plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
            print(f"[成功] 图表已保存: {save_path}")
        
        plt.show()
        
        return {
            'backtest_result': backtest_result,
            'performance': performance,
            'trades': self.backtest_engine.trades
        }
    
    def _display_statistics(self, data, symbol: str):
        """显示基本统计信息"""
        print(f"\n{'=' * 60}")
        print(f"{symbol} 基本统计")
        print(f"{'=' * 60}")
        
        latest = data.iloc[-1]
        if len(data) > 1:
            change_pct = (latest['close'] / data.iloc[-2]['close'] - 1) * 100
        else:
            change_pct = 0
        
        stats = {
            '最新价格': f"{latest['close']:.2f}",
            '涨跌幅': f"{change_pct:.2f}%",
            '最高价': f"{data['high'].max():.2f}",
            '最低价': f"{data['low'].min():.2f}",
            '平均成交量': f"{data['volume'].mean() / 1e6:.2f}M",
            '交易日数': len(data),
            '开始日期': data.index[0].strftime('%Y-%m-%d'),
            '结束日期': data.index[-1].strftime('%Y-%m-%d'),
        }
        
        for key, value in stats.items():
            print(f"{key:>12}: {value}")
    
    def connect_trader(self) -> bool:
        """
        连接交易接口
        
        Returns:
            bool: 是否连接成功
        """
        if not self.enable_trading:
            print("[错误] 交易功能未启用，请在初始化时设置 enable_trading=True")
            return False
        
        return self.trader.connect()
    
    def get_account_info(self):
        """查询账户信息"""
        if not self.enable_trading:
            print("[错误] 交易功能未启用")
            return None
        return self.trader.get_account_info()
    
    def get_positions(self):
        """查询持仓"""
        if not self.enable_trading:
            print("[错误] 交易功能未启用")
            return None
        return self.trader.get_positions()
    
    def buy_stock(self, stock_code: str, price: float, quantity: int):
        """
        买入股票
        
        Args:
            stock_code: 股票代码
            price: 价格（0表示市价）
            quantity: 数量（手）
        """
        if not self.enable_trading:
            print("[错误] 交易功能未启用")
            return None
        return self.trader.buy(stock_code, price, quantity)
    
    def sell_stock(self, stock_code: str, price: float, quantity: int):
        """
        卖出股票
        
        Args:
            stock_code: 股票代码
            price: 价格（0表示市价）
            quantity: 数量（手）
        """
        if not self.enable_trading:
            print("[错误] 交易功能未启用")
            return None
        return self.trader.sell(stock_code, price, quantity)
    
    def select_stocks(self, financial_filters: Dict = None,
                     technical_filters: Dict = None,
                     min_total_score: float = 60.0,
                     max_results: int = 50):
        """
        选股功能
        
        Args:
            financial_filters: 财务筛选条件
            technical_filters: 技术筛选条件
            min_total_score: 最小总分
            max_results: 最大结果数
            
        Returns:
            DataFrame: 选股结果
        """
        return self.stock_selector.select_stocks(
            financial_filters=financial_filters,
            technical_filters=technical_filters,
            min_total_score=min_total_score,
            max_results=max_results
        )
    
    def run_auto_trading(self, stock_code: str, strategy,
                         period: str = "1d", lookback_days: int = 100):
        """
        运行自动交易
        
        Args:
            stock_code: 股票代码
            strategy: 交易策略
            period: 数据周期
            lookback_days: 回看天数
        """
        if not self.enable_trading:
            print("[错误] 交易功能未启用")
            return None
        
        return self.auto_trader.run_strategy(stock_code, strategy, period, lookback_days)
