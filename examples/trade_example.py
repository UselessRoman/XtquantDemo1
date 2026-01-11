# trade_example.py
"""
交易功能使用示例
展示如何使用交易模块进行实盘交易
作者：WJC
日期：2026.1.5
"""

from src.trading.trader import Trader
from src.trading.auto_trader import AutoTrader
from src.strategy.strategies import MACDStrategy, MAStrategy
from examples.main import QuantFramework
import time


def example_1_basic_trading():
    """示例1：基本交易操作"""
    print("\n" + "=" * 60)
    print("示例1：基本交易操作")
    print("=" * 60)
    
    # 配置参数（请根据实际情况修改）
    qmt_path = r'E:\国金QMT交易端模拟\userdata_mini'
    account_id = '8880835625'
    
    # 创建交易接口
    trader = Trader(qmt_path=qmt_path, account_id=account_id)
    
    # 连接交易接口
    if not trader.connect():
        print("[错误] 无法连接交易接口，请确保MiniQMT已启动并登录")
        return
    
    # 1. 查询账户信息
    print("\n【步骤1】查询账户信息")
    print("-" * 60)
    account_info = trader.get_account_info()
    
    # 2. 查询持仓
    print("\n【步骤2】查询持仓")
    print("-" * 60)
    positions = trader.get_positions()
    
    # 3. 买入示例（限价单）
    print("\n【步骤3】买入示例（限价单）")
    print("-" * 60)
    print("注意：以下为示例代码，实际使用时请谨慎操作")
    stock_code = '002352.SZ'
    price = 38.90  # 限价（设置为0表示使用最新价/市价）
    quantity = 1  # 1手（100股）
    # 或者使用目标金额：async_seq = trader.buy(stock_code, target_amount=20000)
    async_seq = trader.buy(stock_code, price, quantity)
    print(f"买入异步序列号: {async_seq}")
    
    # 4. 查询委托
    print("\n【步骤4】查询委托记录")
    print("-" * 60)
    orders = trader.get_orders()
    
    # 5. 查询成交
    print("\n【步骤5】查询成交记录")
    print("-" * 60)
    trades = trader.get_trades()
    
    # 6. 撤单示例
    print("\n【步骤6】撤单示例")
    print("-" * 60)
    print("注意：以下为示例代码")
    # if orders is not None and not orders.empty:
    #     # 获取第一个可撤单的委托
    #     cancelable_orders = trader.get_orders(cancelable_only=True)
    #     if cancelable_orders is not None and not cancelable_orders.empty:
    #         order_id = cancelable_orders.iloc[0]['orderId']
    #         trader.cancel_order(order_id)


def example_2_auto_trading():
    """示例2：自动交易（根据策略信号自动执行）"""
    print("\n" + "=" * 60)
    print("示例2：自动交易")
    print("=" * 60)
    
    # 配置交易参数
    qmt_path = r'D:\qmt\投研\迅投极速交易终端睿智融科版\userdata'
    account_id = '2000128'
    
    # 创建交易接口
    trader = Trader(qmt_path=qmt_path, account_id=account_id)
    
    # 创建自动交易器
    auto_trader = AutoTrader(trader=trader)
    
    # 连接交易接口
    if not auto_trader.connect():
        print("[错误] 无法连接交易接口")
        return
    
    # 创建策略
    strategy = MACDStrategy()
    
    # 运行策略并执行交易
    stock_code = '002352.SZ'
    result = auto_trader.run_strategy(stock_code, strategy, lookback_days=100)
    
    if result['success']:
        print(f"\n[成功] 策略执行成功")
        print(f"  信号: {result.get('signal')}")
        if 'async_seq' in result:
            print(f"  异步序列号: {result['async_seq']}")
    else:
        print(f"\n[错误] 策略执行失败: {result.get('message')}")


def example_3_integrated_framework():
    """示例3：使用完整框架进行交易"""
    print("\n" + "=" * 60)
    print("示例3：使用完整框架进行交易")
    print("=" * 60)
    
    # 配置交易参数
    qmt_path = r'E:\国金QMT交易端模拟\userdata_mini'
    account_id = '8880835625'
    
    # 创建框架（启用交易功能）
    framework = QuantFramework(enable_trading=True, qmt_path=qmt_path, account_id=account_id)
    
    # 连接交易接口
    if not framework.connect_trader():
        print("[错误] 无法连接交易接口")
        return
    
    # 查询账户信息
    print("\n【步骤1】查询账户信息")
    print("-" * 60)
    framework.get_account_info()
    
    # 查询持仓
    print("\n【步骤2】查询持仓")
    print("-" * 60)
    framework.get_positions()
    
    # 运行自动交易
    print("\n【步骤3】运行自动交易")
    print("-" * 60)
    stock_code = '002352.SZ'
    strategy = MAStrategy(use_multiple_ma=True)
    
    result = framework.run_auto_trading(stock_code, strategy, lookback_days=100)
    
    if result and result['success']:
        print(f"\n[成功] 自动交易执行成功")
    else:
        print(f"\n[错误] 自动交易执行失败")


def example_4_position_management():
    """示例4：持仓管理"""
    print("\n" + "=" * 60)
    print("示例4：持仓管理")
    print("=" * 60)
    
    # 配置交易参数
    qmt_path = r'D:\qmt\投研\迅投极速交易终端睿智融科版\userdata'
    account_id = '2000128'
    
    trader = Trader(qmt_path=qmt_path, account_id=account_id)
    
    if not trader.connect():
        print("[错误] 无法连接交易接口")
        return
    
    # 查询持仓
    positions = trader.get_positions()
    
    if positions is not None and not positions.empty:
        print("\n当前持仓列表:")
        for idx, row in positions.iterrows():
            stock_code = row.get('stockCode', row.get('stock_code', 'N/A'))
            print(f"  {stock_code}")
            
            # 查询单个股票的持仓详情
            position = trader.get_position_by_code(stock_code)
            if position:
                print(f"    持仓详情: {position}")
            
            # 卖出全部持仓示例（取消注释以使用）
            # print(f"  准备卖出 {stock_code} 的全部持仓...")
            # order_id = trader.sell_all(stock_code)
            # if order_id:
            #     print(f"  [成功] 卖出委托已提交: {order_id}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("XTquant 交易功能示例")
    print("=" * 60)
    print("\n⚠️  警告：以下示例涉及实盘交易，请谨慎操作！")
    print("⚠️  建议先在模拟环境或小资金测试！")
    print("\n" + "=" * 60)
    
    # 运行示例（根据需要取消注释）
    
    example_1_basic_trading()
    # example_2_auto_trading()
    # example_3_integrated_framework()
    # example_4_position_management()
    
    print("\n提示：取消注释上面的示例函数以运行相应示例")
    print("注意：实际交易前请确保：")
    print("  1. MiniQMT已启动并登录交易账户")
    print("  2. 账户有足够的资金或持仓")
    print("  3. 已在测试环境验证策略有效性")
