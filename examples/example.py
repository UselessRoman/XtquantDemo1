# example.py
"""
使用示例文件
展示框架的各种使用方法
"""

import sys
import os

# 添加项目根目录到路径（确保可以导入 src.* 和 examples.* 模块）
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from examples.main import QuantFramework
from src.strategy.strategies import MACDStrategy, MAStrategy, KDJStrategy, CombinedStrategy


def example_1_basic_usage():
    """示例1：基本使用流程"""
    print("\n" + "=" * 60)
    print("示例1：基本使用流程")
    print("=" * 60)
    
    framework = QuantFramework()
    stock_id = '002352.SZ'
    
    # 下载数据
    framework.download_data(stock_id, '1d', '20250101', '20260110')
    
    # 分析数据
    framework.analyze_data(stock_id, '1d', '20250101', '20260110')
    
    # 运行回测
    strategy = MACDStrategy()
    framework.run_backtest(stock_id, strategy, '1d', '20250101', '20260110')


def example_2_data_management():
    """示例2：数据管理"""
    print("\n" + "=" * 60)
    print("示例2：数据管理")
    print("=" * 60)
    
    from src.data.market_data import MarketDataManager
    
    dm = MarketDataManager()
    stock_id = '002352.SZ'
    
    # 下载数据
    print("\n1. 下载历史数据")
    dm.download_history_data(stock_id, '1d', '20240101', '20241231')
    
    # 获取数据
    print("\n2. 获取本地数据")
    data = dm.get_local_data(stock_id, '1d', '20240101', '20241231')
    if data is not None:
        print(f"   数据条数: {len(data)}")
        print(f"   日期范围: {data.index[0]} 至 {data.index[-1]}")
    
    # 获取数据信息
    print("\n3. 获取数据信息")
    info = dm.get_data_info(stock_id, '1d')
    for key, value in info.items():
        print(f"   {key}: {value}")

    
    # 更新数据
    print("\n5. 更新数据（增量更新）")
    dm.update_data(stock_id, '1d')


def example_3_multiple_strategies():
    """示例3：多策略对比"""
    print("\n" + "=" * 60)
    print("示例3：多策略对比")
    print("=" * 60)
    
    framework = QuantFramework()
    stock_id = '002352.SZ'
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
            stock_id, strategy, '1d', start_date, end_date, save_chart=False
        )
        if result:
            results[name] = result['performance']
    
    # 对比结果
    print("\n" + "=" * 60)
    print("策略对比结果")
    print("=" * 60)
    for name, perf in results.items():
        print(f"\n{name}:")
        print(f"  总收益率: {perf['总收益率']}")
        print(f"  年化收益率: {perf['年化收益率']}")
        print(f"  夏普比率: {perf['夏普比率']}")
        print(f"  最大回撤: {perf['最大回撤']}")


def example_4_combined_strategy():
    """示例4：组合策略"""
    print("\n" + "=" * 60)
    print("示例4：组合策略")
    print("=" * 60)
    
    framework = QuantFramework()
    stock_id = '002352.SZ'
    
    # 创建组合策略：需要至少2个策略同时发出信号
    combined_strategy = CombinedStrategy(
        strategies=[
            MACDStrategy(),
            MAStrategy(use_multiple_ma=True),
            KDJStrategy()
        ],
        vote_threshold=2  # 需要2个策略同时发出信号
    )
    
    result = framework.run_backtest(
        stock_id, combined_strategy, '1d', '20240101', '20241231'
    )


def example_5_batch_download():
    """示例5：批量下载数据"""
    print("\n" + "=" * 60)
    print("示例5：批量下载数据")
    print("=" * 60)
    
    from src.data.market_data import MarketDataManager
    
    dm = MarketDataManager()
    
    # 股票列表
    stock_list = [
        '002352.SZ',
        '000001.SZ',
        '600519.SH',
    ]
    
    # 批量下载
    results = dm.batch_download(
        stock_list, 
        '1d', 
        '20240101', 
        '20241231'
    )
    
    # 显示结果
    print("\n下载结果:")
    for stock_id, success in results.items():
        status = "[成功] 成功" if success else "[错误] 失败"
        print(f"  {stock_id}: {status}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("XTquant 量化交易框架 - 使用示例")
    print("=" * 60)
    
    # 运行示例（根据需要取消注释）
    
    example_1_basic_usage()
    # example_2_data_management()
    # example_3_multiple_strategies()
    # example_4_combined_strategy()
    # example_5_batch_download()
    
    print("\n提示：取消注释上面的示例函数以运行相应示例")
