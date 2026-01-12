# async_trade_monitor_example.py
"""
异步交易+实时监控示例
展示如何使用异步交易并实时监控订单状态
作者：WJC
日期：2026.1.7
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.trading.trader import Trader
from src.trading.trade_monitor import TradeMonitor
import time


def example_1_async_with_monitor():
    """示例1：异步交易+自动监控"""
    print("\n" + "=" * 60)
    print("示例1：异步交易 + 自动监控")
    print("=" * 60)
    
    # 配置参数（请根据实际情况修改）
    qmt_path = r'E:\国金QMT交易端模拟\userdata_mini'
    account_id = '8880835625'
    
    # 创建交易接口
    trader = Trader(qmt_path=qmt_path, account_id=account_id)
    
    # 先连接交易接口（trader.trader 在 connect() 中初始化）
    if not trader.connect():
        print("[错误] 连接失败")
        return
    
    # 创建并注册监控器（必须在 connect() 之后）
    monitor = TradeMonitor()
    trader.trader.register_callback(monitor)
    
    print("\n" + "-" * 60)
    print("步骤1：查询账户和持仓")
    print("-" * 60)
    
    # 查询账户信息
    account_info = trader.get_account_info()
    
    # 查询持仓
    positions = trader.get_positions()
    
    print("\n" + "-" * 60)
    print("步骤2：异步买入（自动监控）")
    print("-" * 60)
    
    # 异步买入（默认async_mode=True）
    stock_code = '001208.SZ'
    seq1 = trader.buy(stock_code, target_amount=10000)  # 买入1万元
    
    if seq1:
        # 注册订单到监控器
        monitor.register_order(seq1, stock_code, 'BUY', 1000, 10.5, '买入测试')
    
    print(f"\n买入请求已提交，请求序号: {seq1}")
    print("监控器将自动跟踪订单状态...")
    
    # 等待一段时间，让监控器接收回调
    print("\n等待5秒，观察监控器输出...")
    time.sleep(5)
    
    print("\n" + "-" * 60)
    print("步骤3：查看监控摘要")
    print("-" * 60)
    
    # 打印监控摘要
    monitor.print_summary()
    
    # 获取统计信息
    stats = monitor.get_statistics()
    print(f"\n当前统计: {stats}")


def example_2_custom_callback():
    """示例2：注册自定义回调函数"""
    print("\n" + "=" * 60)
    print("示例2：注册自定义回调函数")
    print("=" * 60)
    
    qmt_path = r'E:\国金QMT交易端模拟\userdata_mini'
    account_id = '8880835625'
    
    trader = Trader(qmt_path=qmt_path, account_id=account_id)
    
    # 先连接交易接口
    if not trader.connect():
        return
    
    # 创建并注册监控器（必须在 connect() 之后）
    monitor = TradeMonitor()
    trader.trader.register_callback(monitor)
    
    # 定义自定义回调函数
    def on_my_order_confirmed(data):
        """订单确认时的自定义处理"""
        print(f"\n[自定义回调] 订单确认: {data.get('remark', '')}, 订单号: {data.get('order_id', '')}")
    
    def on_my_order_traded(data):
        """订单成交时的自定义处理"""
        print(f"\n[自定义回调] 订单成交: {data.get('direction', '')} {data.get('stock_code', '')} "
              f"{data.get('volume', 0)}股 @ {data.get('price', 0):.2f}元")
    
    # 注册自定义回调
    monitor.register_user_callback('on_order_confirmed', on_my_order_confirmed)
    monitor.register_user_callback('on_order_traded', on_my_order_traded)
    print("\n已注册自定义回调函数")
    
    # 执行异步交易
    print("\n执行异步交易...")
    seq = trader.buy('600000.SH', target_amount=5000)
    
    if seq:
        monitor.register_order(seq, '600000.SH', 'BUY', 500, 10.5, '买入测试')
    
    print("\n等待回调触发...")
    time.sleep(5)
    
    # 打印摘要
    monitor.print_summary()


def example_3_batch_async_trade():
    """示例3：批量异步交易"""
    print("\n" + "=" * 60)
    print("示例3：批量异步交易")
    print("=" * 60)
    
    qmt_path = r'E:\国金QMT交易端模拟\userdata_mini'
    account_id = '8880835625'
    
    trader = Trader(qmt_path=qmt_path, account_id=account_id)
    
    # 先连接交易接口
    if not trader.connect():
        return
    
    # 创建并注册监控器（必须在 connect() 之后）
    monitor = TradeMonitor()
    trader.trader.register_callback(monitor)
    
    # 批量买入多只股票
    stocks = [
        ('600000.SH', 5000),   # 浦发银行，买入5000元
        ('600519.SH', 10000),  # 贵州茅台，买入10000元
        ('000001.SZ', 3000),   # 平安银行，买入3000元
    ]
    
    print("\n开始批量异步交易...")
    seqs = []
    
    for stock_code, amount in stocks:
        seq = trader.buy(stock_code, target_amount=amount)
        if seq:
            monitor.register_order(seq, stock_code, 'BUY', 0, 0, f'批量买入{stock_code}')
            seqs.append((stock_code, seq))
            print(f"[成功] {stock_code}: seq={seq}")
        time.sleep(0.5)  # 稍微延迟，避免请求过快
    
    print(f"\n共提交 {len(seqs)} 个买入请求")
    print("监控器正在实时跟踪所有订单...")
    
    # 等待所有订单处理
    print("\n等待10秒，观察监控器输出...")
    time.sleep(10)
    
    # 打印最终摘要
    monitor.print_summary()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("异步交易 + 实时监控示例")
    print("=" * 60)
    print("\n注意：")
    print("1. 请先配置正确的 QMT 路径和账户ID")
    print("2. 确保 MiniQMT 已启动并登录")
    print("3. 建议先在模拟环境测试")
    print("=" * 60)
    
    # 运行示例（根据需要取消注释）
    example_1_async_with_monitor()
    # example_2_custom_callback()
    # example_3_batch_async_trade()
    
    print("\n提示：取消注释上面的示例函数以运行相应示例")
