# example.py
"""
基础使用示例
展示框架的基本使用方法
"""

import sys
import os

# 添加项目根目录到路径（确保可以导入 src.* 和 examples.* 模块）
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from examples.main import QuantFramework
from src.strategy.strategies import MACDStrategy, MAStrategy, KDJStrategy, CombinedStrategy
import pandas as pd


def example_1_basic_usage():
    """示例1：基本使用流程（数据 → 分析 → 回测）"""
    print("\n" + "=" * 60)
    print("示例1：基本使用流程")
    print("=" * 60)
    
    framework = QuantFramework()
    stock_id = '002352.SZ'
    
    # 1. 下载数据
    print("\n【步骤1】下载历史数据")
    print("-" * 60)
    framework.download_data(stock_id, '1d', '20240101', '20241231')
    
    # 2. 分析数据
    print("\n【步骤2】分析数据并绘制图表")
    print("-" * 60)
    framework.analyze_data(stock_id, '1d', '20240101', '20241231', save_chart=False)
    
    # 3. 运行回测
    print("\n【步骤3】运行策略回测")
    print("-" * 60)
    strategy = MACDStrategy()
    framework.run_backtest(stock_id, strategy, '1d', '20240101', '20241231', save_chart=False)


def example_2_data_management():
    """示例2：数据管理功能"""
    print("\n" + "=" * 60)
    print("示例2：数据管理")
    print("=" * 60)
    
    from src.data.market_data import MarketDataManager
    from src.data.financial_data import FinancialDataManager
    
    # 行情数据管理
    print("\n【行情数据管理】")
    print("-" * 60)
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
        print(f"   日期范围: {data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}")
    
    # 更新数据
    print("\n3. 增量更新数据")
    dm.update_data(stock_id, '1d')
    
    # 财务数据管理
    print("\n【财务数据管理】")
    print("-" * 60)
    fm = FinancialDataManager()
    
    print("\n4. 获取财务数据")
    financial_data = fm.get_financial_data('600519.SH', auto_download=False)
    if financial_data:
        print(f"   PE: {financial_data.get('pe', 'N/A')}")
        print(f"   ROE: {financial_data.get('roe', 'N/A')}")


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
        print(f"  总收益率: {perf.get('总收益率', 'N/A')}")
        print(f"  年化收益率: {perf.get('年化收益率', 'N/A')}")
        print(f"  夏普比率: {perf.get('夏普比率', 'N/A')}")
        print(f"  最大回撤: {perf.get('最大回撤', 'N/A')}")


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
        stock_id, combined_strategy, '1d', '20240101', '20241231', save_chart=False
    )


def example_5_batch_operations():
    """示例5：批量操作"""
    print("\n" + "=" * 60)
    print("示例5：批量操作")
    print("=" * 60)
    
    from src.data.market_data import MarketDataManager
    from src.data.financial_data import FinancialDataManager
    
    # 批量下载行情数据
    print("\n【批量下载行情数据】")
    print("-" * 60)
    dm = MarketDataManager()
    stock_list = ['002352.SZ', '000001.SZ', '600519.SH']
    results = dm.batch_download(stock_list, '1d', '20240101', '20241231')
    for stock_id, success in results.items():
        status = "[成功]" if success else "[失败]"
        print(f"  {stock_id}: {status}")
    
    # 批量获取财务数据
    print("\n【批量获取财务数据】")
    print("-" * 60)
    fm = FinancialDataManager()
    all_financial = fm.batch_get_financial_data(stock_list, auto_download=False)
    for code, data in all_financial.items():
        if data:
            print(f"  {code}: PE={data.get('pe', 'N/A')}, ROE={data.get('roe', 'N/A')}")


def example_6_stock_selection():
    """示例6：选股功能"""
    print("\n" + "=" * 60)
    print("示例6：选股功能")
    print("=" * 60)
    
    framework = QuantFramework()
    
    # 使用框架的选股功能
    selected = framework.select_stocks(
        financial_filters={
            'max_pe': 30,
            'min_roe': 10,
            'min_profit_growth': 5
        },
        technical_filters={
            'min_technical_score': 40,
            'require_above_ma20': True
        },
        min_total_score=60.0,
        max_results=10
    )
    
    if selected is not None and not selected.empty:
        print(f"\n选出 {len(selected)} 只股票:")
        for idx, row in selected.head(5).iterrows():
            print(f"  {row['stock_code']}: 总分={row['total_score']:.2f}")
    else:
        print("未选出符合条件的股票")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("XTquant 量化交易框架 - 基础使用示例")
    print("=" * 60)
    print("\n本文件包含基础功能示例")
    print("查看 complete_example.py 获取完整功能示例\n")
    
    # 运行示例（根据需要取消注释）
    example_1_basic_usage()
    # example_2_data_management()
    # example_3_multiple_strategies()
    # example_4_combined_strategy()
    # example_5_batch_operations()
    # example_6_stock_selection()
    
    print("\n提示：")
    print("1. 取消注释上面的示例函数以运行相应示例")
    print("2. 查看 complete_example.py 获取所有功能的完整示例")
    print("3. 查看其他 example 文件了解特定功能的详细用法")
