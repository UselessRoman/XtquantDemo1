# strategy_example.py
"""
策略功能示例
展示如何使用各种交易策略
"""

import sys
import os

# 添加项目根目录到路径
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from examples.main import QuantFramework
from src.strategy.strategies import MACDStrategy, MAStrategy, KDJStrategy, RSIStrategy, CombinedStrategy
import pandas as pd


def example_single_strategy():
    """示例1：单个策略使用"""
    print("\n" + "=" * 60)
    print("示例1：单个策略使用")
    print("=" * 60)
    
    framework = QuantFramework()
    stock_code = '002352.SZ'
    
    # 获取数据
    data = framework.get_data(stock_code, '1d', '20240101', '20241231')
    if data is None or data.empty:
        print("[错误] 无法获取数据")
        return
    
    # 计算指标
    indicators = framework.indicator_calculator.calculate_all(data)
    
    # MACD策略
    print("\n【MACD策略】")
    print("-" * 60)
    macd_strategy = MACDStrategy()
    signals = macd_strategy.generate_signals(data, indicators)
    buy_count = (signals == 1).sum()
    sell_count = (signals == -1).sum()
    print(f"买入信号: {buy_count} 次")
    print(f"卖出信号: {sell_count} 次")
    
    # 均线策略
    print("\n【均线策略】")
    print("-" * 60)
    ma_strategy = MAStrategy(use_multiple_ma=True)
    signals_ma = ma_strategy.generate_signals(data, indicators)
    buy_count_ma = (signals_ma == 1).sum()
    print(f"买入信号: {buy_count_ma} 次")
    
    # KDJ策略
    print("\n【KDJ策略】")
    print("-" * 60)
    kdj_strategy = KDJStrategy()
    signals_kdj = kdj_strategy.generate_signals(data, indicators)
    buy_count_kdj = (signals_kdj == 1).sum()
    print(f"买入信号: {buy_count_kdj} 次")


def example_combined_strategy():
    """示例2：组合策略"""
    print("\n" + "=" * 60)
    print("示例2：组合策略")
    print("=" * 60)
    
    framework = QuantFramework()
    stock_code = '002352.SZ'
    
    # 获取数据
    data = framework.get_data(stock_code, '1d', '20240101', '20241231')
    if data is None or data.empty:
        print("[错误] 无法获取数据")
        return
    
    # 计算指标
    indicators = framework.indicator_calculator.calculate_all(data)
    
    # 创建组合策略：需要至少2个策略同时发出信号
    print("\n【组合策略：需要至少2个策略同意】")
    print("-" * 60)
    combined_strategy = CombinedStrategy(
        strategies=[
            MACDStrategy(),
            MAStrategy(use_multiple_ma=True),
            KDJStrategy()
        ],
        vote_threshold=2  # 需要2个策略同时发出信号
    )
    signals_combined = combined_strategy.generate_signals(data, indicators)
    buy_count_combined = (signals_combined == 1).sum()
    sell_count_combined = (signals_combined == -1).sum()
    print(f"买入信号: {buy_count_combined} 次")
    print(f"卖出信号: {sell_count_combined} 次")
    print("说明: 只有当至少2个策略同时发出买入/卖出信号时，才会产生交易信号")


def example_strategy_comparison():
    """示例3：策略对比"""
    print("\n" + "=" * 60)
    print("示例3：策略对比")
    print("=" * 60)
    
    framework = QuantFramework()
    stock_code = '002352.SZ'
    
    strategies = [
        ('MACD策略', MACDStrategy()),
        ('均线策略', MAStrategy(use_multiple_ma=True)),
        ('KDJ策略', KDJStrategy()),
    ]
    
    results = {}
    for name, strategy in strategies:
        print(f"\n运行策略: {name}")
        result = framework.run_backtest(
            stock_code, strategy, '1d', '20240101', '20241231', save_chart=False
        )
        if result:
            results[name] = result['performance']
    
    # 对比结果
    if results:
        print("\n" + "=" * 60)
        print("策略对比结果")
        print("=" * 60)
        print(f"{'策略名称':<12} {'总收益率':<12} {'年化收益率':<14} {'夏普比率':<12}")
        print("-" * 60)
        for name, perf in results.items():
            print(f"{name:<12} {str(perf.get('总收益率', 'N/A')):<12} "
                  f"{str(perf.get('年化收益率', 'N/A')):<14} "
                  f"{str(perf.get('夏普比率', 'N/A')):<12}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("策略功能示例")
    print("=" * 60)
    
    # 运行示例（根据需要取消注释）
    example_single_strategy()
    # example_combined_strategy()
    # example_strategy_comparison()
    
    print("\n提示：取消注释上面的示例函数以运行相应示例")
