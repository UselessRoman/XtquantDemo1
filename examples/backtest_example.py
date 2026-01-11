# backtest_example.py
"""
回测功能示例
展示如何使用策略回测功能
"""

import sys
import os

# 添加项目根目录到路径
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from examples.main import QuantFramework
from src.strategy.strategies import MACDStrategy, MAStrategy, KDJStrategy, CombinedStrategy


def example_single_backtest():
    """示例1：单个策略回测"""
    print("\n" + "=" * 60)
    print("示例1：单个策略回测")
    print("=" * 60)
    
    framework = QuantFramework()
    stock_code = '002352.SZ'
    
    # 运行回测
    strategy = MACDStrategy()
    result = framework.run_backtest(
        stock_code, strategy, '1d', '20240101', '20241231', save_chart=False
    )
    
    if result:
        print("\n回测性能指标:")
        for key, value in result['performance'].items():
            print(f"  {key}: {value}")
        
        print(f"\n交易次数: {len(result['trades'])}")


def example_multiple_backtest():
    """示例2：多策略回测对比"""
    print("\n" + "=" * 60)
    print("示例2：多策略回测对比")
    print("=" * 60)
    
    framework = QuantFramework()
    stock_code = '002352.SZ'
    start_date = '20240101'
    end_date = '20241231'
    
    strategies = [
        ('MACD策略', MACDStrategy()),
        ('均线策略', MAStrategy(use_multiple_ma=True)),
        ('KDJ策略', KDJStrategy()),
    ]
    
    results = {}
    for name, strategy in strategies:
        print(f"\n运行策略: {name}")
        result = framework.run_backtest(
            stock_code, strategy, '1d', start_date, end_date, save_chart=False
        )
        if result:
            results[name] = result['performance']
    
    # 对比结果
    if results:
        print("\n" + "=" * 60)
        print("策略对比结果")
        print("=" * 60)
        print(f"{'策略名称':<12} {'总收益率':<12} {'年化收益率':<14} {'夏普比率':<12} {'最大回撤':<12}")
        print("-" * 60)
        for name, perf in results.items():
            print(f"{name:<12} {str(perf.get('总收益率', 'N/A')):<12} "
                  f"{str(perf.get('年化收益率', 'N/A')):<14} "
                  f"{str(perf.get('夏普比率', 'N/A')):<12} "
                  f"{str(perf.get('最大回撤', 'N/A')):<12}")


def example_combined_backtest():
    """示例3：组合策略回测"""
    print("\n" + "=" * 60)
    print("示例3：组合策略回测")
    print("=" * 60)
    
    framework = QuantFramework()
    stock_code = '002352.SZ'
    
    # 创建组合策略
    combined_strategy = CombinedStrategy(
        strategies=[
            MACDStrategy(),
            MAStrategy(use_multiple_ma=True),
            KDJStrategy()
        ],
        vote_threshold=2  # 需要2个策略同时发出信号
    )
    
    result = framework.run_backtest(
        stock_code, combined_strategy, '1d', '20240101', '20241231', save_chart=False
    )
    
    if result:
        print("\n组合策略回测结果:")
        for key, value in result['performance'].items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("回测功能示例")
    print("=" * 60)
    
    # 运行示例（根据需要取消注释）
    example_single_backtest()
    # example_multiple_backtest()
    # example_combined_backtest()
    
    print("\n提示：取消注释上面的示例函数以运行相应示例")
