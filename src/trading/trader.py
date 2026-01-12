# trader.py
"""
交易模块
功能：实盘交易功能，包括下单、撤单、查询等
基于 XtQuantTrader API
作者：WJC
日期：2026.1.5
"""

from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from xtquant import xtconstant
from xtquant import xtdata
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time
import warnings
import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.utils import validate_stock_code, format_number
from src.core.config import TradeConfig

warnings.filterwarnings('ignore')


class TraderCallback(XtQuantTraderCallback):
    """交易回调类：处理交易接口的各种回调事件"""
    
    def __init__(self):
        """初始化回调类"""
        self.order_callbacks = []
        self.trade_callbacks = []
        self.error_callbacks = []
    
    def on_disconnected(self):
        """连接断开回调"""
        print(f"[回调] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 连接断开")
    
    def on_stock_order(self, order):
        """委托回报推送"""
        order_info = {
            'order_id': getattr(order, 'order_id', ''),
            'stock_code': getattr(order, 'stock_code', ''),
            'order_status': getattr(order, 'order_status', ''),
            'order_remark': getattr(order, 'order_remark', ''),
            'order_time': getattr(order, 'order_time', ''),
            'price': getattr(order, 'price', 0),
            'volume': getattr(order, 'volume', 0),
        }
        print(f"[回调] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 委托回报: {order_info['order_remark']}")
        for callback in self.order_callbacks:
            try:
                callback(order_info)
            except:
                pass
    
    def on_stock_trade(self, trade):
        """成交变动推送"""
        trade_info = {
            'trade_id': getattr(trade, 'trade_id', ''),
            'order_id': getattr(trade, 'order_id', 0),
            'stock_code': getattr(trade, 'stock_code', ''),
            'order_remark': getattr(trade, 'order_remark', ''),
            'offset_flag': getattr(trade, 'offset_flag', 0),  # OFFSET_FLAG_OPEN=48(买入), OFFSET_FLAG_CLOSE=49(卖出)
            'traded_price': getattr(trade, 'traded_price', 0.0),
            'traded_volume': getattr(trade, 'traded_volume', 0),
            'traded_time': getattr(trade, 'traded_time', 0),
            'traded_amount': getattr(trade, 'traded_amount', 0.0),  # 成交金额
        }
        # 根据官方文档，使用 xtconstant 中的交易操作常量
        # OFFSET_FLAG_OPEN (48) = 买入/开仓，OFFSET_FLAG_CLOSE (49) = 卖出/平仓
        offset_flag = trade_info['offset_flag']
        if offset_flag == xtconstant.OFFSET_FLAG_OPEN:
            direction = '买入'
        elif offset_flag == xtconstant.OFFSET_FLAG_CLOSE:
            direction = '卖出'
        else:
            direction = '其他'
        print(f"[回调] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 成交回报: {trade_info['order_remark']} "
              f"{direction} 价格 {trade_info['traded_price']} 数量 {trade_info['traded_volume']}")
        for callback in self.trade_callbacks:
            try:
                callback(trade_info)
            except:
                pass
    
    def on_order_error(self, order_error):
        """委托失败推送"""
        error_info = {
            'order_id': getattr(order_error, 'order_id', ''),
            'error_id': getattr(order_error, 'error_id', ''),
            'error_msg': getattr(order_error, 'error_msg', ''),
            'order_remark': getattr(order_error, 'order_remark', ''),
        }
        print(f"[回调] 委托报错: {error_info['order_remark']} {error_info['error_msg']}")
        for callback in self.error_callbacks:
            try:
                callback(error_info)
            except:
                pass
    
    def on_cancel_error(self, cancel_error):
        """撤单失败推送"""
        print(f"[回调] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 撤单失败")
    
    def on_order_stock_async_response(self, response):
        """异步下单回报推送"""
        remark = getattr(response, 'order_remark', '')
        print(f"[回调] 异步委托回调: {remark}")
    
    def on_cancel_order_stock_async_response(self, response):
        """异步撤单回报推送"""
        print(f"[回调] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 异步撤单回调")
    
    def on_account_status(self, status):
        """账户状态回调"""
        print(f"[回调] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 账户状态变更")


class Trader:
    """交易类：封装XtQuantTrader的交易功能"""
    
    def __init__(self, qmt_path: str = None, account_id: str = None, 
                 account_type: str = 'STOCK', session_id: int = None):
        """
        初始化交易接口
        
        Args:
            qmt_path: QMT客户端路径，如果为None则使用TradeConfig中的配置
            account_id: 资金账号，如果为None则使用TradeConfig中的配置
            account_type: 账户类型，'STOCK'股票账号, 'CREDIT'信用, 'FUTURE'期货
            session_id: 会话ID，如果为None则自动生成
        """
        self.qmt_path = qmt_path or TradeConfig.QMT_PATH
        self.account_id = account_id or TradeConfig.ACCOUNT_ID
        self.account_type = account_type
        self.session_id = session_id or int(time.time())
        
        self.trader = None
        self.account = None
        self.callback = None
        self.is_connected = False
        self.is_subscribed = False
    
    def connect(self) -> bool:
        """
        连接交易接口
        
        Returns:
            bool: 是否连接成功
        """
        try:
            if not self.qmt_path:
                print("[错误] 未配置QMT路径，请在TradeConfig中设置QMT_PATH或传入qmt_path参数")
                return False
            
            if not self.account_id:
                print("[错误] 未配置账户ID，请在TradeConfig中设置ACCOUNT_ID或传入account_id参数")
                return False
            
            # 创建交易接口
            print(f"[信息] 初始化交易接口，路径: {self.qmt_path}, Session ID: {self.session_id}")
            self.trader = XtQuantTrader(self.qmt_path, self.session_id)
            
            # 创建账户对象
            self.account = StockAccount(self.account_id, self.account_type)
            
            # 创建并注册回调
            if TradeConfig.ENABLE_CALLBACK:
                self.callback = TraderCallback()
                self.trader.register_callback(self.callback)
            
            # 启动交易线程
            self.trader.start()
            
            # 建立交易连接
            connect_result = self.trader.connect()
            if connect_result == 0:
                self.is_connected = True
                print("[成功] 交易接口连接成功")
                
                # 订阅交易回调
                subscribe_result = self.trader.subscribe(self.account)
                if subscribe_result == 0:
                    self.is_subscribed = True
                    print("[成功] 交易回调订阅成功")
                else:
                    print(f"[警告] 交易回调订阅失败，返回码: {subscribe_result}")
                
                return True
            else:
                print(f"[错误] 交易接口连接失败，返回码: {connect_result}")
                print("提示: 请确保MiniQMT已启动并登录交易账户")
                self.is_connected = False
                return False
                
        except Exception as e:
            print(f"[错误] 连接交易接口失败: {e}")
            traceback.print_exc()
            self.is_connected = False
            return False
    
    def get_account_info(self) -> Optional[Dict]:
        """
        查询账户信息
        
        Returns:
            Dict: 账户信息，包含资金、可用资金等
        """
        if not self.is_connected:
            if not self.connect():
                return None
        
        try:
            account_info = self.trader.query_stock_asset(self.account)
            
            if account_info:
                # 根据官方文档，XtAsset 的属性为：
                # cash (float) - 可用金额
                # frozen_cash (float) - 冻结金额
                # market_value (float) - 持仓市值
                # total_asset (float) - 总资产
                # 使用 getattr 安全获取属性（兼容不同版本）
                total_asset = getattr(account_info, 'total_asset', 0)
                cash = getattr(account_info, 'cash', 0)
                frozen_cash = getattr(account_info, 'frozen_cash', 0)
                market_value = getattr(account_info, 'market_value', 0)
                
                # 总盈亏 = 总资产 - 初始资金（这里简化为总资产 - 可用资金 - 持仓市值）
                # 实际上盈亏应该通过持仓来计算，这里只做简单估算
                profit = total_asset - cash - market_value
                
                result = {
                    'account_id': self.account_id,
                    '总资产': total_asset,
                    '可用资金': cash,
                    '冻结资金': frozen_cash,
                    '持仓市值': market_value,
                    '总盈亏': profit,
                }
                
                print("\n账户信息:")
                print("=" * 60)
                for key, value in result.items():
                    if isinstance(value, (int, float)):
                        if '资金' in key or '资产' in key or '市值' in key or '盈亏' in key:
                            print(f"  {key}: {format_number(value, 2)}")
                        else:
                            print(f"  {key}: {value}")
                    else:
                        print(f"  {key}: {value}")
                print("=" * 60)
                return result
            else:
                print("[错误] 无法获取账户信息")
                return None
                
        except Exception as e:
            print(f"[错误] 查询账户信息失败: {e}")
            traceback.print_exc()
            return None
    
    def get_positions(self) -> Optional[pd.DataFrame]:
        """
        查询持仓信息
        
        Returns:
            DataFrame: 持仓信息
        """
        if not self.is_connected:
            if not self.connect():
                return None
        
        try:
            positions = self.trader.query_stock_positions(self.account)
            
            if positions:
                # 根据官方文档，XtPosition 的属性为：
                # volume (int) - 持仓数量
                # can_use_volume (int) - 可用数量
                # open_price (float) - 开仓价（返回与成本价一致）
                # market_value (float) - 市值
                # avg_price (float) - 成本价
                # frozen_volume (int) - 冻结数量
                # 转换为DataFrame
                position_list = []
                for pos in positions:
                    # 使用 getattr 安全获取属性
                    volume = getattr(pos, 'volume', 0)
                    can_use_volume = getattr(pos, 'can_use_volume', 0)
                    frozen_volume = getattr(pos, 'frozen_volume', 0)
                    avg_price = getattr(pos, 'avg_price', 0)
                    open_price = getattr(pos, 'open_price', avg_price)  # 开仓价，如果没有则用成本价
                    market_value = getattr(pos, 'market_value', 0)
                    stock_code = getattr(pos, 'stock_code', '')
                    
                    # 计算盈亏 = 市值 - 成本
                    cost = volume * avg_price
                    profit = market_value - cost
                    
                    position_dict = {
                        '股票代码': stock_code,
                        '总持仓(股)': volume,
                        '可用(股)': can_use_volume,
                        '冻结(股)': frozen_volume,
                        '成本价': avg_price,
                        '开仓价': open_price,
                        '市值(元)': market_value,
                        '盈亏(元)': profit,
                    }
                    position_list.append(position_dict)
                
                df = pd.DataFrame(position_list)
                
                if not df.empty:
                    print("\n持仓信息:")
                    print("=" * 100)
                    # 手动格式化输出，确保对齐
                    # 定义列宽
                    widths = {
                        '股票代码': 12,
                        '总持仓(股)': 12,
                        '可用(股)': 12,
                        '冻结(股)': 12,
                        '成本价': 10,
                        '开仓价': 10,
                        '市值(元)': 15,
                        '盈亏(元)': 15,
                    }
                    
                    # 格式化标题行
                    header = (
                        f"{'股票代码':<{widths['股票代码']}}"
                        f"{'总持仓(股)':>{widths['总持仓(股)']}}"
                        f"{'可用(股)':>{widths['可用(股)']}}"
                        f"{'冻结(股)':>{widths['冻结(股)']}}"
                        f"{'成本价':>{widths['成本价']}}"
                        f"{'开仓价':>{widths['开仓价']}}"
                        f"{'市值(元)':>{widths['市值(元)']}}"
                        f"{'盈亏(元)':>{widths['盈亏(元)']}}"
                    )
                    print(header)
                    print("-" * 100)
                    
                    # 格式化数据行
                    for _, row in df.iterrows():
                        stock_code = str(row['股票代码'])
                        volume = int(row['总持仓(股)'])
                        can_use = int(row['可用(股)'])
                        frozen = int(row['冻结(股)'])
                        cost_price = f"{row['成本价']:.2f}"
                        open_price = f"{row['开仓价']:.2f}"
                        market_value = f"{row['市值(元)']:,.2f}"
                        profit = f"{row['盈亏(元)']:,.2f}"
                        
                        line = (
                            f"{stock_code:<{widths['股票代码']}}"
                            f"{volume:>{widths['总持仓(股)']}}"
                            f"{can_use:>{widths['可用(股)']}}"
                            f"{frozen:>{widths['冻结(股)']}}"
                            f"{cost_price:>{widths['成本价']}}"
                            f"{open_price:>{widths['开仓价']}}"
                            f"{market_value:>{widths['市值(元)']}}"
                            f"{profit:>{widths['盈亏(元)']}}"
                        )
                        print(line)
                    
                    print("=" * 100)
                    return df  # 返回原始 DataFrame，包含原始数值类型
                else:
                    print("当前无持仓")
                    return pd.DataFrame()
            else:
                print("当前无持仓")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"[错误] 查询持仓失败: {e}")
            traceback.print_exc()
            return None
    
    def buy(self, stock_code: str, price: float = 0, quantity: int = None,
            target_amount: float = None, price_type: int = None, 
            async_mode: bool = True) -> Optional[int]:
        """
        买入股票
        
        Args:
            stock_code: 股票代码，如 '002352.SZ'
            price: 买入价格（限价单时使用），0表示使用最新价或市价
            quantity: 买入数量（手，1手=100股），如果指定则优先使用
            target_amount: 目标买入金额（元），如果指定则按金额计算数量
            price_type: 价格类型，xtconstant.FIX_PRICE限价，xtconstant.LATEST_PRICE最新价
            async_mode: 是否使用异步模式，True=异步下单，False=同步下单
            
        Returns:
            int: 异步模式返回请求序号seq，同步模式返回订单编号order_id，失败返回None
        """
        if not self.is_connected:
            if not self.connect():
                return None
        
        # 验证股票代码
        if not validate_stock_code(stock_code):
            print(f"[错误] 股票代码格式错误: {stock_code}")
            return None
        
        try:
            # 确定价格类型和价格
            if price_type is None:
                if price > 0:
                    price_type = xtconstant.FIX_PRICE  # 限价
                    order_price = price
                else:
                    price_type = xtconstant.LATEST_PRICE  # 最新价
                    order_price = -1
            
            # 确定买入数量
            if quantity is None:
                if target_amount:
                    # 按目标金额计算
                    account_info = self.trader.query_stock_asset(self.account)
                    if not account_info:
                        print("[错误] 无法获取账户信息")
                        return None
                    
                    available_cash = getattr(account_info, 'cash', 0)
                    
                    # 获取最新价
                    full_tick = xtdata.get_full_tick([stock_code])
                    if stock_code in full_tick:
                        current_price = full_tick[stock_code]['lastPrice']
                    else:
                        print(f"[错误] 无法获取 {stock_code} 的最新价")
                        return None
                    
                    # 买入金额取目标金额与可用金额中较小的
                    buy_amount = min(target_amount, available_cash)
                    # 买入数量取整为100的整数倍（手）
                    quantity_shares = int(buy_amount / current_price / 100) * 100
                    quantity = quantity_shares // 100  # 转换为手
                    order_price = current_price
                    
                    print(f"当前可用资金 {format_number(available_cash, 2)} "
                          f"目标买入金额 {format_number(target_amount, 2)} "
                          f"买入股数 {quantity_shares}股 ({quantity}手)")
                else:
                    print("[错误] 请指定 quantity（数量）或 target_amount（目标金额）")
                    return None
            
            if quantity <= 0:
                print("[错误] 买入数量必须大于0")
                return None
            
            # 转换为股数
            volume = quantity * 100
            
            order_remark = f"买入{stock_code}"
            
            # 根据模式选择同步或异步下单
            if async_mode:
                # 异步下单：立即返回请求序号seq，实际结果通过回调获取
                result = self.trader.order_stock_async(
                    self.account, stock_code, xtconstant.STOCK_BUY, volume,
                    price_type, order_price, 'strategy_name', order_remark
                )
            else:
                # 同步下单：等待服务器响应，立即返回订单编号order_id
                result = self.trader.order_stock(
                    self.account, stock_code, xtconstant.STOCK_BUY, volume,
                    price_type, order_price, 'strategy_name', order_remark
                )
            
            if result and result > 0:
                price_str = format_number(order_price, 2) if order_price > 0 else "最新价"
                mode_str = "异步" if async_mode else "同步"
                result_name = "请求序号seq" if async_mode else "订单编号order_id"
                print(f"[成功] 买入委托已提交（{mode_str}模式）")
                print(f"  股票: {stock_code}")
                print(f"  价格: {price_str}")
                print(f"  数量: {quantity} 手 ({volume} 股)")
                print(f"  {result_name}: {result}")
                return result
            else:
                print("[错误] 买入委托提交失败")
                return None
                
        except Exception as e:
            print(f"[错误] 买入失败: {e}")
            traceback.print_exc()
            return None
    
    def sell(self, stock_code: str, price: float = 0, quantity: int = None,
             price_type: int = None, async_mode: bool = True) -> Optional[int]:
        """
        卖出股票
        
        Args:
            stock_code: 股票代码
            price: 卖出价格（限价单时使用），0表示使用最新价或市价
            quantity: 卖出数量（手，1手=100股），如果为None则卖出全部可用持仓
            price_type: 价格类型，xtconstant.FIX_PRICE限价，xtconstant.LATEST_PRICE最新价
            async_mode: 是否使用异步模式，True=异步下单，False=同步下单
            
        Returns:
            int: 异步模式返回请求序号seq，同步模式返回订单编号order_id，失败返回None
        """
        if not self.is_connected:
            if not self.connect():
                return None
        
        # 验证股票代码
        if not validate_stock_code(stock_code):
            print(f"[错误] 股票代码格式错误: {stock_code}")
            return None
        
        try:
            # 获取可用持仓
            positions = self.trader.query_stock_positions(self.account)
            if not positions:
                print(f"[错误] 未持有股票 {stock_code}")
                return None
            
            # 查找指定股票的持仓
            available_volume = 0
            for pos in positions:
                if pos.stock_code == stock_code:
                    available_volume = pos.m_nCanUseVolume
                    break
            
            if available_volume <= 0:
                print(f"[错误] 股票 {stock_code} 无可用持仓")
                return None
            
            # 确定卖出数量
            if quantity is None:
                # 卖出全部可用持仓
                quantity = available_volume // 100  # 转换为手
            else:
                # 卖出数量不能超过可用持仓
                quantity = min(quantity, available_volume // 100)
            
            if quantity <= 0:
                print(f"[错误] 卖出数量必须大于0")
                return None
            
            # 确定价格类型和价格
            if price_type is None:
                if price > 0:
                    price_type = xtconstant.FIX_PRICE  # 限价
                    order_price = price
                else:
                    price_type = xtconstant.LATEST_PRICE  # 最新价
                    order_price = -1
            
            # 转换为股数
            volume = quantity * 100
            
            order_remark = f"卖出{stock_code}"
            
            # 根据模式选择同步或异步下单
            if async_mode:
                # 异步下单：立即返回请求序号seq，实际结果通过回调获取
                result = self.trader.order_stock_async(
                    self.account, stock_code, xtconstant.STOCK_SELL, volume,
                    price_type, order_price, 'strategy_name', order_remark
                )
            else:
                # 同步下单：等待服务器响应，立即返回订单编号order_id
                result = self.trader.order_stock(
                    self.account, stock_code, xtconstant.STOCK_SELL, volume,
                    price_type, order_price, 'strategy_name', order_remark
                )
            
            if result and result > 0:
                price_str = format_number(order_price, 2) if order_price > 0 else "最新价"
                mode_str = "异步" if async_mode else "同步"
                result_name = "请求序号seq" if async_mode else "订单编号order_id"
                print(f"[成功] 卖出委托已提交（{mode_str}模式）")
                print(f"  股票: {stock_code}")
                print(f"  价格: {price_str}")
                print(f"  数量: {quantity} 手 ({volume} 股)")
                print(f"  {result_name}: {result}")
                return result
            else:
                print("[错误] 卖出委托提交失败")
                return None
                
        except Exception as e:
            print(f"[错误] 卖出失败: {e}")
            traceback.print_exc()
            return None
    
    def cancel_order(self, order_id: int, async_mode: bool = True) -> bool:
        """
        撤销委托
        
        Args:
            order_id: 委托编号（同步下单返回的order_id）
            async_mode: 是否使用异步模式，True=异步撤单，False=同步撤单
            
        Returns:
            bool: 同步模式返回是否成功（0成功，-1失败），异步模式返回是否提交成功（seq>0成功）
        """
        if not self.is_connected:
            if not self.connect():
                return False
        
        try:
            if async_mode:
                # 异步撤单：立即返回请求序号seq，实际结果通过回调获取
                seq = self.trader.cancel_order_stock_async(self.account, order_id)
                if seq and seq > 0:
                    print(f"[成功] 撤单请求已提交（异步模式）: 订单编号 {order_id}, 请求序号 {seq}")
                    return True
                else:
                    print(f"[错误] 撤单请求提交失败: {order_id}")
                    return False
            else:
                # 同步撤单：等待服务器响应，立即返回结果（0成功，-1失败）
                result = self.trader.cancel_order_stock(self.account, order_id)
                if result == 0:
                    print(f"[成功] 撤单成功（同步模式）: 订单编号 {order_id}")
                    return True
                else:
                    print(f"[错误] 撤单失败: 订单编号 {order_id}, 返回码 {result}")
                    return False
                
        except Exception as e:
            print(f"[错误] 撤单失败: {e}")
            traceback.print_exc()
            return False
    
    def get_orders(self, cancelable_only: bool = False) -> Optional[pd.DataFrame]:
        """
        查询委托记录
        
        Args:
            cancelable_only: 是否只查询可撤单的委托
            
        Returns:
            DataFrame: 委托记录
        """
        if not self.is_connected:
            if not self.connect():
                return None
        
        try:
            orders = self.trader.query_stock_orders(self.account)
            
            if orders:
                # 转换为DataFrame
                order_list = []
                for order in orders:
                    # 根据官方文档，XtOrder 的属性为：
                    # order_id (int) - 订单编号
                    # stock_code (str) - 证券代码
                    # order_status (int) - 委托状态
                    # price (float) - 委托价格
                    # order_volume (int) - 委托数量
                    # traded_volume (int) - 成交数量
                    # traded_price (float) - 成交均价
                    # order_time (int) - 报单时间
                    order_dict = {
                        'order_id': getattr(order, 'order_id', 0),
                        'stock_code': getattr(order, 'stock_code', ''),
                        'order_status': getattr(order, 'order_status', 0),
                        'price': getattr(order, 'price', 0.0),
                        'volume': getattr(order, 'order_volume', 0),  # 委托数量
                        'traded_volume': getattr(order, 'traded_volume', 0),
                        'traded_price': getattr(order, 'traded_price', 0.0),
                        'order_time': getattr(order, 'order_time', 0),
                        'order_remark': getattr(order, 'order_remark', ''),
                    }
                    order_list.append(order_dict)
                
                df = pd.DataFrame(order_list)
                
                if not df.empty:
                    # 如果只查询可撤单的，过滤状态
                    if cancelable_only:
                        # 可撤单状态：已报(ORDER_REPORTED)、部成待撤(ORDER_PARTSUCC_CANCEL)
                        if 'order_status' in df.columns:
                            # 只查询可撤单的状态：已报、部成待撤
                            df = df[df['order_status'].isin([
                                xtconstant.ORDER_REPORTED,           # 50: 已报
                                xtconstant.ORDER_PARTSUCC_CANCEL     # 52: 部成待撤
                            ])]
                    
                    print("\n委托记录:")
                    print("=" * 60)
                    print(df.to_string(index=False))
                    print("=" * 60)
                    return df
                else:
                    print("当前无委托记录")
                    return pd.DataFrame()
            else:
                print("当前无委托记录")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"[错误] 查询委托失败: {e}")
            traceback.print_exc()
            return None
    
    def get_trades(self) -> Optional[pd.DataFrame]:
        """
        查询成交记录
        
        Returns:
            DataFrame: 成交记录
        """
        if not self.is_connected:
            if not self.connect():
                return None
        
        try:
            trades = self.trader.query_stock_trades(self.account)
            
            if trades:
                # 转换为DataFrame
                trade_list = []
                for trade in trades:
                    # 根据官方文档，XtTrade 的属性为：
                    # order_id (int) - 订单编号
                    # stock_code (str) - 证券代码
                    # traded_price (float) - 成交均价
                    # traded_volume (int) - 成交数量
                    # traded_amount (float) - 成交金额
                    # traded_time (int) - 成交时间
                    # offset_flag (int) - 交易操作
                    offset_flag = getattr(trade, 'offset_flag', 0)
                    # 根据官方文档，使用 xtconstant 中的交易操作常量
                    if offset_flag == xtconstant.OFFSET_FLAG_OPEN:
                        direction = '买入'
                    elif offset_flag == xtconstant.OFFSET_FLAG_CLOSE:
                        direction = '卖出'
                    else:
                        direction = '其他'
                    
                    trade_dict = {
                        'trade_id': getattr(trade, 'traded_id', ''),  # 成交编号
                        'order_id': getattr(trade, 'order_id', 0),
                        'stock_code': getattr(trade, 'stock_code', ''),
                        'offset_flag': offset_flag,  # OFFSET_FLAG_OPEN=48(买入), OFFSET_FLAG_CLOSE=49(卖出)
                        'direction': direction,
                        'traded_price': getattr(trade, 'traded_price', 0.0),
                        'traded_volume': getattr(trade, 'traded_volume', 0),
                        'traded_amount': getattr(trade, 'traded_amount', 0.0),
                        'traded_time': getattr(trade, 'traded_time', 0),
                        'order_remark': getattr(trade, 'order_remark', ''),
                    }
                    trade_list.append(trade_dict)
                
                df = pd.DataFrame(trade_list)
                
                if not df.empty:
                    print("\n成交记录:")
                    print("=" * 60)
                    print(df.to_string(index=False))
                    print("=" * 60)
                    return df
                else:
                    print("当前无成交记录")
                    return pd.DataFrame()
            else:
                print("当前无成交记录")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"[错误] 查询成交失败: {e}")
            traceback.print_exc()
            return None
    
    def get_position_by_code(self, stock_code: str) -> Optional[Dict]:
        """
        查询指定股票的持仓
        
        Args:
            stock_code: 股票代码
            
        Returns:
            Dict: 持仓信息，无持仓返回None
        """
        positions = self.get_positions()
        
        if positions is None or positions.empty:
            return None
        
        # 查找指定股票
        pos = positions[positions['stock_code'] == stock_code]
        
        if not pos.empty:
            return pos.iloc[0].to_dict()
        else:
            return None
    
    def sell_all(self, stock_code: str, price: float = 0,
                 price_type: int = None) -> Optional[int]:
        """
        卖出指定股票的全部可用持仓
        
        Args:
            stock_code: 股票代码
            price: 卖出价格，0表示最新价
            price_type: 价格类型
            
        Returns:
            int: 异步下单序列号，失败返回None
        """
        # 传入 quantity=None 表示卖出全部
        return self.sell(stock_code, price, quantity=None, price_type=price_type)
    
    def get_account_summary(self) -> Dict:
        """
        获取账户摘要信息
        
        Returns:
            Dict: 账户摘要
        """
        account_info = self.get_account_info()
        positions = self.get_positions()
        
        summary = {
            'account_info': account_info,
            'position_count': len(positions) if positions is not None and not positions.empty else 0,
            'has_positions': positions is not None and not positions.empty
        }
        
        return summary
    
    def register_order_callback(self, callback_func):
        """注册委托回调函数"""
        if self.callback:
            self.callback.order_callbacks.append(callback_func)
    
    def register_trade_callback(self, callback_func):
        """注册成交回调函数"""
        if self.callback:
            self.callback.trade_callbacks.append(callback_func)
    
    def register_error_callback(self, callback_func):
        """注册错误回调函数"""
        if self.callback:
            self.callback.error_callbacks.append(callback_func)
