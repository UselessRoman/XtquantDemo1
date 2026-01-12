# ml_strategy_example.py
"""
ML多因子策略使用示例
展示如何使用机器学习多因子策略进行选股和交易
作者：WJC
日期：2026.1.12
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.selection.selector import MLStockSelector
from src.trading.auto_trader import MLAutoTrader
from src.trading.trader import Trader
from src.trading.trade_monitor import TradeMonitor
from src.strategy.strategies import MLMultiFactorStrategy
import time


def example_1_ml_stock_selection():
    """示例1：ML选股"""
    print("\n" + "=" * 60)
    print("示例1：ML选股")
    print("=" * 60)
    
    # 模型文件路径（相对于项目根目录）
    model_path = 'model_2024_multiclass.pkl'
    
    # 创建ML选股器
    selector = MLStockSelector(
        model_path=model_path,
        stock_num=7,  # 选择7只股票
        score_threshold=0.61  # 得分阈值
    )
    
    # 执行选股
    end_date = datetime.now().strftime('%Y%m%d')
    print(f"\n开始ML选股（截止日期: {end_date}）...")
    
    selected_stocks, scores = selector.select_stocks_ml(end_date)
    
    if selected_stocks:
        print(f"\n[成功] 选出 {len(selected_stocks)} 只股票:")
        print("-" * 60)
        for stock, score in zip(selected_stocks, scores):
            print(f"  {stock}: 得分={score:.4f}")
        print("-" * 60)
        return selected_stocks, scores
    else:
        print("\n[信息] 未选出符合条件的股票")
        return [], []


def example_2_ml_strategy_backtest():
    """示例2：ML策略回测（简化版）"""
    print("\n" + "=" * 60)
    print("示例2：ML策略回测")
    print("=" * 60)
    print("\n注意：ML策略是组合策略，需要同时考虑多只股票")
    print("完整的回测需要在回测引擎中实现多股票组合逻辑")
    print("\n这里仅展示策略的基本使用方法：")
    
    model_path = 'model_2024_multiclass.pkl'
    strategy = MLMultiFactorStrategy(model_path, stock_num=7)
    
    # 执行选股
    selected_stocks, scores = strategy.select_stocks_for_backtest()
    
    if selected_stocks:
        print(f"\n选中的股票: {selected_stocks}")
        print(f"对应得分: {[f'{s:.4f}' for s in scores]}")
    else:
        print("\n未选出股票")


def example_3_ml_auto_trading():
    """示例3：ML策略自动交易"""
    print("\n" + "=" * 60)
    print("示例3：ML策略自动交易")
    print("=" * 60)
    print("\n⚠️  注意：此示例需要连接MiniQMT")
    
    # 配置参数
    qmt_path = r'E:\国金QMT交易端模拟\userdata_mini'
    account_id = '8880835625'
    model_path = 'model_2024_multiclass.pkl'
    
    # 创建交易接口
    trader = Trader(qmt_path=qmt_path, account_id=account_id)
    
    # 创建ML选股器
    selector = MLStockSelector(model_path=model_path, stock_num=7, score_threshold=0.61)
    
    # 创建ML自动交易器
    ml_trader = MLAutoTrader(trader=trader, selector=selector, stock_num=7)
    
    # 连接交易接口
    if not ml_trader.connect():
        print("[错误] 连接交易接口失败")
        return
    
    # 注册交易监控器
    monitor = TradeMonitor()
    trader.trader.register_callback(monitor)
    
    print("\n步骤1: ML选股")
    print("-" * 60)
    end_date = datetime.now().strftime('%Y%m%d')
    selected_stocks, scores = selector.select_stocks_ml(end_date)
    
    if not selected_stocks:
        print("[错误] 未选出股票")
        return
    
    print(f"选出 {len(selected_stocks)} 只股票:")
    for stock, score in zip(selected_stocks, scores):
        print(f"  {stock}: 得分={score:.4f}")
    
    print("\n步骤2: 执行调仓")
    print("-" * 60)
    result = ml_trader.rebalance_portfolio(selected_stocks, scores, end_date)
    
    if result['success']:
        print(f"调仓完成:")
        print(f"  卖出: {result['sold']}")
        print(f"  买入: {result['bought']}")
    
    print("\n步骤3: 查询持仓")
    print("-" * 60)
    positions = trader.get_positions()
    
    print("\n提示: 策略支持定时调仓和风控检查")
    print("  调仓: 每月1日和15日")
    print("  风控: ATR止损、RSRS风控")


def example_4_risk_control():
    """示例4：风控检查"""
    print("\n" + "=" * 60)
    print("示例4：风控检查")
    print("=" * 60)
    
    from src.strategy.risk_control import RiskController
    
    risk_controller = RiskController()
    
    # 检查市场择时
    print("\n1. 检查市场择时（RSRS）")
    print("-" * 60)
    can_open = risk_controller.check_market_timing()
    market_rsrs = risk_controller.calculate_market_rsrs()
    print(f"市场RSRS: {market_rsrs:.4f}")
    print(f"允许开仓: {'是' if can_open else '否'}")
    
    # 检查个股RSRS
    print("\n2. 检查个股RSRS")
    print("-" * 60)
    test_stock = '600000.SH'
    stock_rsrs = risk_controller.calculate_rsrs(test_stock)
    print(f"{test_stock} RSRS: {stock_rsrs:.4f}")
    if stock_rsrs < -0.7:
        print("  ⚠️  RSRS < -0.7，建议卖出")
    
    # 计算ATR止损位
    print("\n3. 计算ATR止损")
    print("-" * 60)
    atr = risk_controller.calculate_atr(test_stock)
    print(f"{test_stock} ATR: {atr:.2f}")
    
    # 假设当前最高价为12.0
    current_high = 12.0
    stop_loss = risk_controller.calculate_stop_loss_level(test_stock, current_high)
    print(f"止损位（最高价{current_high} - 2*ATR）: {stop_loss:.2f}")


def example_5_complete_workflow():
    """示例5：完整工作流程"""
    print("\n" + "=" * 80)
    print("示例5：完整工作流程（选股 → 调仓 → 风控）")
    print("=" * 80)
    print("\n⚠️  注意：此示例需要连接MiniQMT")
    
    # 配置参数
    qmt_path = r'E:\国金QMT交易端模拟\userdata_mini'
    account_id = '8880835625'
    model_path = 'model_2024_multiclass.pkl'
    
    # 创建组件
    trader = Trader(qmt_path=qmt_path, account_id=account_id)
    selector = MLStockSelector(model_path=model_path, stock_num=7, score_threshold=0.61)
    ml_trader = MLAutoTrader(trader=trader, selector=selector, stock_num=7)
    
    # 连接
    if not ml_trader.connect():
        print("[错误] 连接失败")
        return
    
    # 注册监控器
    monitor = TradeMonitor()
    trader.trader.register_callback(monitor)
    
    # 完整流程
    end_date = datetime.now().strftime('%Y%m%d')
    
    print("\n【步骤1】ML选股")
    print("-" * 80)
    selected_stocks, scores = selector.select_stocks_ml(end_date)
    if not selected_stocks:
        print("未选出股票，流程结束")
        return
    
    print("\n【步骤2】市场择时检查")
    print("-" * 80)
    if not ml_trader.check_market_timing(end_date):
        print("市场弱势，禁止开仓")
        return
    
    print("\n【步骤3】执行调仓")
    print("-" * 80)
    rebalance_result = ml_trader.rebalance_portfolio(selected_stocks, scores, end_date)
    
    print("\n【步骤4】更新涨停股列表")
    print("-" * 80)
    ml_trader.update_limit_up_list(end_date)
    print(f"昨日涨停股票: {ml_trader.yesterday_limit_up_list}")
    
    print("\n【步骤5】风控检查")
    print("-" * 80)
    triggered_stocks, cash_released = ml_trader.check_risk_control(end_date)
    if triggered_stocks:
        print(f"触发风控的股票: {triggered_stocks}")
        print(f"释放现金: {cash_released:.2f} 元")
        
        # 再投资
        if cash_released > 0:
            print("\n【步骤6】再投资")
            print("-" * 80)
            reinvested = ml_trader.reinvest(selected_stocks, scores, cash_released, end_date)
            if reinvested:
                print(f"再投资股票: {reinvested}")
    
    print("\n【步骤7】查看持仓")
    print("-" * 80)
    positions = trader.get_positions()
    
    print("\n" + "=" * 80)
    print("完整流程执行完成")
    print("=" * 80)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ML多因子策略使用示例")
    print("=" * 60)
    print("\n注意：")
    print("1. 确保模型文件 model_2024_multiclass.pkl 在项目根目录")
    print("2. 交易相关示例需要连接MiniQMT")
    print("3. 建议先在模拟环境测试")
    print("=" * 60)
    
    # 运行示例（根据需要取消注释）
    example_1_ml_stock_selection()
    # example_2_ml_strategy_backtest()
    # example_3_ml_auto_trading()
    # example_4_risk_control()
    # example_5_complete_workflow()
    
    print("\n提示：取消注释上面的示例函数以运行相应示例")
