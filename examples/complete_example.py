# complete_example.py
"""
完整功能示例
整合所有模块功能的完整使用示例
作者：WJC
日期：2026.1.7
"""

import sys
import os

# 添加项目根目录到路径
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from examples.main import QuantFramework
from src.data.market_data import MarketDataManager
from src.data.financial_data import FinancialDataManager
from src.analysis.technical import TechnicalIndicators, ChartPlotter
from src.analysis.fundamental import FundamentalAnalyzer
from src.strategy.strategies import MACDStrategy, MAStrategy, KDJStrategy, RSIStrategy, CombinedStrategy
from src.backtest.engine import BacktestEngine
from src.backtest.analyzer import PerformanceAnalyzer
from src.selection.selector import StockSelector
from src.trading.trader import Trader
from src.trading.auto_trader import AutoTrader
import pandas as pd
import time


# ==================== 数据管理示例 ====================

def example_data_market():
    """示例：行情数据管理"""
    print("\n" + "=" * 60)
    print("【功能示例】行情数据管理")
    print("=" * 60)
    
    manager = MarketDataManager()
    stock_code = '002352.SZ'
    
    # 1. 下载历史数据
    print("\n1. 下载历史数据")
    print("-" * 60)
    success = manager.download_history_data(
        stock_code, '1d', '20240101', '20241231'
    )
    print(f"下载结果: {'成功' if success else '失败'}")
    
    # 2. 获取本地数据
    print("\n2. 获取本地数据")
    print("-" * 60)
    data = manager.get_local_data(stock_code, '1d', '20240101', '20241231')
    if data is not None:
        print(f"数据条数: {len(data)}")
        print(f"日期范围: {data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}")
        print(f"最新收盘价: {data['close'].iloc[-1]:.2f}")
    
    # 3. 增量更新数据
    print("\n3. 增量更新数据")
    print("-" * 60)
    update_success = manager.update_data(stock_code, '1d')
    print(f"更新结果: {'成功' if update_success else '失败'}")
    
    # 4. 批量下载
    print("\n4. 批量下载数据")
    print("-" * 60)
    stock_list = ['002352.SZ', '600519.SH', '000001.SZ']
    results = manager.batch_download(stock_list, '1d', '20240101', '20241231')
    for code, success in results.items():
        print(f"  {code}: {'成功' if success else '失败'}")


def example_data_financial():
    """示例：财务数据管理"""
    print("\n" + "=" * 60)
    print("【功能示例】财务数据管理")
    print("=" * 60)
    
    manager = FinancialDataManager()
    stock_code = '600519.SH'
    
    # 1. 获取财务数据（自动下载）
    print(f"\n1. 获取 {stock_code} 的财务数据")
    print("-" * 60)
    financial_data = manager.get_financial_data(stock_code, auto_download=True)
    if financial_data:
        print("财务指标:")
        for key, value in financial_data.items():
            if isinstance(value, (int, float)):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
    else:
        print("未能获取财务数据")
    
    # 2. 批量获取财务数据
    print("\n2. 批量获取财务数据")
    print("-" * 60)
    stock_list = ['600519.SH', '000001.SZ', '002352.SZ']
    all_data = manager.batch_get_financial_data(stock_list, auto_download=False)
    for code, data in all_data.items():
        if data:
            pe = data.get('pe', 'N/A')
            roe = data.get('roe', 'N/A')
            print(f"  {code}: PE={pe}, ROE={roe}")


# ==================== 分析示例 ====================

def example_technical_analysis():
    """示例：技术指标分析"""
    print("\n" + "=" * 60)
    print("【功能示例】技术指标分析")
    print("=" * 60)
    
    manager = MarketDataManager()
    calculator = TechnicalIndicators()
    stock_code = '002352.SZ'
    
    # 获取数据
    data = manager.get_local_data(stock_code, '1d')
    if data is None or data.empty:
        print("[错误] 无法获取数据，请先下载数据")
        return
    
    # 计算所有技术指标
    print("\n1. 计算技术指标")
    print("-" * 60)
    indicators = calculator.calculate_all(data)
    print("已计算指标: MA、MACD、KDJ")
    
    # 显示最新指标值
    if 'ma' in indicators and not indicators['ma'].empty:
        latest_ma = indicators['ma'].iloc[-1]
        print("\n最新均线值:")
        for col in ['MA5', 'MA10', 'MA20']:
            if col in latest_ma and not pd.isna(latest_ma[col]):
                print(f"  {col}: {latest_ma[col]:.2f}")
    
    # 绘制图表
    print("\n2. 绘制技术分析图表")
    print("-" * 60)
    plotter = ChartPlotter()
    try:
        fig, axes = plotter.create_chart(data, indicators, stock_code)
        print("[成功] 图表已生成")
        import matplotlib.pyplot as plt
        plt.close(fig)
    except Exception as e:
        print(f"[提示] 图表生成跳过: {e}")


def example_fundamental_analysis():
    """示例：财务指标分析"""
    print("\n" + "=" * 60)
    print("【功能示例】财务指标分析")
    print("=" * 60)
    
    manager = FinancialDataManager()
    analyzer = FundamentalAnalyzer()
    stock_code = '600519.SH'
    
    # 获取财务数据
    financial_data = manager.get_financial_data(stock_code, auto_download=False)
    if not financial_data:
        print("[错误] 无法获取财务数据")
        return
    
    # 计算财务得分
    print("\n1. 计算财务得分")
    print("-" * 60)
    score_result = analyzer.calculate_financial_score(financial_data)
    if score_result:
        print(f"财务得分: {score_result['score']}/{score_result['max_score']}")
        print("得分详情:")
        for key, value in score_result['details'].items():
            print(f"  {key}: {value}")
    
    # 财务数据筛选
    print("\n2. 财务数据筛选")
    print("-" * 60)
    filters = {
        'max_pe': 30,
        'min_roe': 10,
        'min_profit_growth': 5
    }
    passed = analyzer.filter_financial_data(financial_data, filters)
    print(f"筛选结果: {'通过' if passed else '未通过'}")


# ==================== 策略示例 ====================

def example_strategies():
    """示例：策略使用"""
    print("\n" + "=" * 60)
    print("【功能示例】交易策略")
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
    
    # 1. MACD策略
    print("\n1. MACD策略")
    print("-" * 60)
    macd_strategy = MACDStrategy()
    signals = macd_strategy.generate_signals(data, indicators)
    buy_count = (signals == 1).sum()
    sell_count = (signals == -1).sum()
    print(f"买入信号: {buy_count} 次")
    print(f"卖出信号: {sell_count} 次")
    
    # 2. 均线策略
    print("\n2. 均线策略")
    print("-" * 60)
    ma_strategy = MAStrategy(use_multiple_ma=True)
    signals_ma = ma_strategy.generate_signals(data, indicators)
    buy_count_ma = (signals_ma == 1).sum()
    print(f"买入信号: {buy_count_ma} 次")
    
    # 3. 组合策略
    print("\n3. 组合策略")
    print("-" * 60)
    combined = CombinedStrategy(
        strategies=[MACDStrategy(), MAStrategy(use_multiple_ma=True), KDJStrategy()],
        vote_threshold=2
    )
    signals_combined = combined.generate_signals(data, indicators)
    buy_count_combined = (signals_combined == 1).sum()
    print(f"买入信号: {buy_count_combined} 次（需要至少2个策略同时发出信号）")


# ==================== 回测示例 ====================

def example_backtest():
    """示例：策略回测"""
    print("\n" + "=" * 60)
    print("【功能示例】策略回测")
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


# ==================== 选股示例 ====================

def example_stock_selection():
    """示例：选股功能"""
    print("\n" + "=" * 60)
    print("【功能示例】选股功能")
    print("=" * 60)
    
    selector = StockSelector()
    
    # 选股条件
    financial_filters = {
        'max_pe': 30,
        'min_roe': 10,
        'min_profit_growth': 5
    }
    
    technical_filters = {
        'min_technical_score': 40,
        'require_above_ma20': True
    }
    
    print("\n执行选股...")
    result = selector.select_stocks(
        financial_filters=financial_filters,
        technical_filters=technical_filters,
        min_total_score=60.0,
        max_results=10
    )
    
    if result is not None and not result.empty:
        print(f"\n选出 {len(result)} 只股票:")
        for idx, row in result.head(5).iterrows():
            print(f"  {row['stock_code']}: 总分={row['total_score']:.2f}, "
                  f"财务={row['financial_score']:.2f}, 技术={row['technical_score']:.2f}")
    else:
        print("未选出符合条件的股票")


# ==================== 交易示例 ====================

def example_trading_basic():
    """示例：基础交易功能"""
    print("\n" + "=" * 60)
    print("【功能示例】基础交易功能")
    print("=" * 60)
    print("\n⚠️  注意：以下为示例代码，实际交易需要连接MiniQMT")
    
    # 注意：此示例不会实际执行，仅展示用法
    print("\n代码示例:")
    print("-" * 60)
    print("""
    # 创建交易接口
    trader = Trader(
        qmt_path=r'D:\\qmt\\...\\userdata',
        account_id='2000128'
    )
    
    # 连接
    if trader.connect():
        # 查询账户
        account_info = trader.get_account_info()
        
        # 异步买入（默认模式）
        seq = trader.buy('600000.SH', target_amount=10000)
        
        # 查询持仓
        positions = trader.get_positions()
    """)


def example_trading_auto():
    """示例：自动交易"""
    print("\n" + "=" * 60)
    print("【功能示例】自动交易")
    print("=" * 60)
    print("\n⚠️  注意：此功能需要连接MiniQMT")
    
    print("\n代码示例:")
    print("-" * 60)
    print("""
    # 使用框架的自动交易功能
    framework = QuantFramework(
        enable_trading=True,
        qmt_path=r'D:\\qmt\\...\\userdata',
        account_id='2000128'
    )
    
    # 连接
    framework.connect_trader()
    
    # 运行自动交易
    strategy = MACDStrategy()
    result = framework.run_auto_trading('002352.SZ', strategy, lookback_days=100)
    """)


# ==================== 完整流程示例 ====================

def example_complete_workflow():
    """示例：完整量化交易流程"""
    print("\n" + "=" * 80)
    print("【完整流程示例】量化交易完整流程")
    print("=" * 80)
    
    framework = QuantFramework()
    stock_code = '002352.SZ'
    start_date = '20240101'
    end_date = '20241231'
    
    print("\n步骤1: 下载历史数据")
    print("-" * 80)
    framework.download_data(stock_code, '1d', start_date, end_date)
    
    print("\n步骤2: 获取并查看数据")
    print("-" * 80)
    data = framework.get_data(stock_code, '1d', start_date, end_date)
    if data is not None:
        print(f"数据条数: {len(data)}")
        print(f"最新价格: {data['close'].iloc[-1]:.2f}")
    
    print("\n步骤3: 技术分析")
    print("-" * 80)
    framework.analyze_data(stock_code, '1d', start_date, end_date, save_chart=False)
    
    print("\n步骤4: 策略回测")
    print("-" * 80)
    strategy = MACDStrategy()
    backtest_result = framework.run_backtest(
        stock_code, strategy, '1d', start_date, end_date, save_chart=False
    )
    
    print("\n步骤5: 多策略对比")
    print("-" * 80)
    strategies = {
        'MACD': MACDStrategy(),
        'MA': MAStrategy(use_multiple_ma=True),
        'KDJ': KDJStrategy(),
    }
    
    results_comparison = {}
    for name, strat in strategies.items():
        result = framework.run_backtest(
            stock_code, strat, '1d', start_date, end_date, save_chart=False
        )
        if result:
            results_comparison[name] = result['performance']
    
    # 对比结果
    if results_comparison:
        print("\n策略对比:")
        print(f"{'策略':<10} {'总收益率':<12} {'年化收益率':<14} {'夏普比率':<12}")
        print("-" * 60)
        for name, perf in results_comparison.items():
            print(f"{name:<10} {perf.get('总收益率', 'N/A'):<12} "
                  f"{perf.get('年化收益率', 'N/A'):<14} {perf.get('夏普比率', 'N/A'):<12}")
    
    print("\n" + "=" * 80)
    print("完整流程示例完成")
    print("=" * 80)


def example_complete_with_trading():
    """示例：完整流程（包含交易）"""
    print("\n" + "=" * 80)
    print("【完整流程示例】选股 → 回测 → 交易")
    print("=" * 80)
    print("\n⚠️  注意：此示例包含实盘交易，请谨慎操作")
    
    # 配置参数（需要根据实际情况修改）
    qmt_path = r'D:\qmt\投研\迅投极速交易终端睿智融科版\userdata'
    account_id = '2000128'
    
    print("\n步骤1: 选股")
    print("-" * 80)
    selector = StockSelector()
    selected = selector.select_stocks(
        financial_filters={'max_pe': 30, 'min_roe': 10},
        min_total_score=60.0,
        max_results=5
    )
    
    if selected is None or selected.empty:
        print("未选出股票，流程结束")
        return
    
    print(f"\n选出 {len(selected)} 只股票:")
    for idx, row in selected.head(3).iterrows():
        print(f"  {row['stock_code']}: 总分={row['total_score']:.2f}")
    
    print("\n步骤2: 对选出的股票进行回测")
    print("-" * 80)
    framework = QuantFramework()
    strategy = MACDStrategy()
    
    for idx, row in selected.head(3).iterrows():
        stock = row['stock_code']
        print(f"\n回测 {stock}...")
        result = framework.run_backtest(
            stock, strategy, '1d', '20240101', '20241231', save_chart=False
        )
        if result:
            total_return = result['performance'].get('总收益率', 'N/A')
            print(f"  总收益率: {total_return}")
    
    print("\n步骤3: 自动交易（需要连接MiniQMT）")
    print("-" * 80)
    print("代码示例:")
    print("""
    # 启用交易功能
    framework = QuantFramework(
        enable_trading=True,
        qmt_path=qmt_path,
        account_id=account_id
    )
    
    # 连接
    framework.connect_trader()
    
    # 对选出的股票执行自动交易
    for stock in selected_stocks:
        framework.run_auto_trading(stock, strategy, lookback_days=100)
    """)


# ==================== 主函数 ====================

def main():
    """运行所有示例"""
    print("\n" + "=" * 80)
    print("XTquant 量化交易框架 - 完整功能示例")
    print("=" * 80)
    print("\n本文件展示了框架的所有核心功能")
    print("可以根据需要运行相应的示例函数\n")
    
    # 数据管理示例
    example_data_market()
    example_data_financial()
    
    # 分析示例
    example_technical_analysis()
    example_fundamental_analysis()
    
    # 策略示例
    example_strategies()
    
    # 回测示例
    example_backtest()
    
    # 选股示例
    example_stock_selection()
    
    # 交易示例（仅展示代码，不实际执行）
    example_trading_basic()
    example_trading_auto()
    
    # 完整流程示例
    example_complete_workflow()
    example_complete_with_trading()
    
    print("\n" + "=" * 80)
    print("所有示例运行完成")
    print("=" * 80)
    print("\n提示:")
    print("1. 可以根据需要单独运行某个示例函数")
    print("2. 交易相关示例需要连接MiniQMT客户端")
    print("3. 建议先在测试环境验证策略后再实盘交易")


if __name__ == "__main__":
    main()
