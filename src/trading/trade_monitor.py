# trade_monitor.py
"""
交易监控模块
功能：实时监控异步交易状态，管理订单生命周期
作者：WJC
日期：2026.1.5
"""

from xtquant.xttrader import XtQuantTraderCallback
from xtquant import xtconstant
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
import pandas as pd
import threading


class TradeMonitor(XtQuantTraderCallback):
    """
    交易监控器：实时监控异步交易状态
    继承自 XtQuantTraderCallback，实现各种回调方法
    """
    
    def __init__(self):
        """初始化交易监控器"""
        super().__init__()
        
        # 订单跟踪字典
        self.pending_orders = {}  # 待处理订单
        self.confirmed_orders = {}  # 已确认订单
        self.completed_orders = {}  # 已完成订单
        
        # 成交记录
        self.trade_records = defaultdict(list)
        
        # 错误记录
        self.error_records = []
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'confirmed': 0,
            'completed': 0,
            'failed': 0,
            'total_traded_amount': 0.0,
        }
        
        # 线程锁
        self.lock = threading.Lock()
        
        # 用户回调
        self.user_callbacks = {
            'on_order_confirmed': [],
            'on_order_traded': [],
            'on_order_completed': [],
            'on_order_error': [],
        }
    
    def register_order(self, seq: int, stock_code: str, order_type: str, 
                      volume: int, price: float, remark: str = ''):
        """注册异步订单到监控器"""
        with self.lock:
            self.pending_orders[seq] = {
                'seq': seq,
                'stock_code': stock_code,
                'order_type': order_type,
                'volume': volume,
                'price': price,
                'remark': remark,
                'submit_time': datetime.now(),
                'status': 'PENDING',
                'order_id': None,
            }
            self.stats['total_requests'] += 1
            
        print(f"[监控] 注册异步订单: seq={seq}, {order_type} {stock_code} "
              f"{volume}股@{price if price > 0 else '最新价'}")
    
    def on_stock_order(self, order):
        """委托回报"""
        with self.lock:
            order_id = getattr(order, 'order_id', '')
            stock_code = getattr(order, 'stock_code', '')
            order_status = getattr(order, 'order_status', 0)
            order_remark = getattr(order, 'order_remark', '')
            
            # 根据官方文档，使用 xtconstant 中的委托状态常量
            status_map = {
                xtconstant.ORDER_UNREPORTED: '未报',           # 48
                xtconstant.ORDER_WAIT_REPORTING: '待报',       # 49
                xtconstant.ORDER_REPORTED: '已报',             # 50
                xtconstant.ORDER_REPORTED_CANCEL: '已报待撤',  # 51
                xtconstant.ORDER_PARTSUCC_CANCEL: '部成待撤',  # 52
                xtconstant.ORDER_PART_CANCEL: '部撤',          # 53
                xtconstant.ORDER_CANCELED: '已撤',             # 54
                xtconstant.ORDER_PART_SUCC: '部成',            # 55
                xtconstant.ORDER_SUCCEEDED: '已成',            # 56
                xtconstant.ORDER_JUNK: '废单',                 # 57
                xtconstant.ORDER_UNKNOWN: '未知',              # 255
            }
            status_name = status_map.get(order_status, f'状态{order_status}')
            
            if order_id not in self.confirmed_orders:
                order_data = {
                    'order_id': order_id,
                    'stock_code': stock_code,
                    'order_status': order_status,
                    'remark': order_remark,
                    'update_time': datetime.now(),
                }
                self.confirmed_orders[order_id] = order_data
                self.stats['confirmed'] += 1
                # 触发用户回调
                self._trigger_user_callback('on_order_confirmed', order_data)
            else:
                self.confirmed_orders[order_id]['order_status'] = order_status
                self.confirmed_orders[order_id]['update_time'] = datetime.now()
            
            print(f"[监控] 📋 委托回报: {order_remark} | 订单{order_id} | 状态:{status_name}")
            
            # 订单完成状态：已撤、已成、废单
            if order_status in [xtconstant.ORDER_CANCELED, xtconstant.ORDER_SUCCEEDED, xtconstant.ORDER_JUNK]:
                self._mark_completed(order_id, status_name)
    
    def on_stock_trade(self, trade):
        """成交回报"""
        with self.lock:
            # 根据官方文档，XtTrade 的属性为：
            # order_id (int) - 订单编号
            # stock_code (str) - 证券代码
            # traded_price (float) - 成交均价
            # traded_volume (int) - 成交数量
            # traded_amount (float) - 成交金额
            # offset_flag (int) - 交易操作，48=买入，49=卖出
            order_id = getattr(trade, 'order_id', 0)
            stock_code = getattr(trade, 'stock_code', '')
            traded_price = getattr(trade, 'traded_price', 0.0)
            traded_volume = getattr(trade, 'traded_volume', 0)
            offset_flag = getattr(trade, 'offset_flag', 0)
            
            # 根据官方文档，使用 xtconstant 中的交易操作常量
            # OFFSET_FLAG_OPEN (48) = 买入/开仓，OFFSET_FLAG_CLOSE (49) = 卖出/平仓
            if offset_flag == xtconstant.OFFSET_FLAG_OPEN:
                direction = '买入'
            elif offset_flag == xtconstant.OFFSET_FLAG_CLOSE:
                direction = '卖出'
            else:
                # 其他类型（强平、平今、平昨等）
                direction = '其他'
            # 使用 traded_amount 如果存在，否则计算
            traded_amount = getattr(trade, 'traded_amount', None)
            if traded_amount is None:
                amount = traded_price * traded_volume
            else:
                amount = traded_amount
            
            trade_data = {
                'order_id': order_id,
                'stock_code': stock_code,
                'direction': direction,
                'price': traded_price,
                'volume': traded_volume,
                'amount': amount,
            }
            self.trade_records[order_id].append(trade_data)
            self.stats['total_traded_amount'] += amount
            
            # 触发用户回调
            self._trigger_user_callback('on_order_traded', trade_data)
            
            print(f"[监控] 💰 成交: {direction} {stock_code} {traded_volume}股@{traded_price:.2f}")
    
    def on_order_error(self, order_error):
        """委托失败"""
        with self.lock:
            error_msg = getattr(order_error, 'error_msg', '')
            error_data = {'error_msg': error_msg, 'time': datetime.now()}
            self.error_records.append(error_data)
            self.stats['failed'] += 1
            # 触发用户回调
            self._trigger_user_callback('on_order_error', error_data)
            print(f"[监控] ❌ 委托失败: {error_msg}")
    
    def _mark_completed(self, order_id: str, status: str):
        """标记订单完成"""
        if order_id in self.confirmed_orders:
            order = self.confirmed_orders[order_id].copy()
            order['final_status'] = status
            self.completed_orders[order_id] = order
            self.stats['completed'] += 1
            # 触发用户回调
            self._trigger_user_callback('on_order_completed', order)
    
    def print_summary(self):
        """打印监控摘要"""
        print("\n" + "=" * 60)
        print("交易监控摘要")
        print("=" * 60)
        print(f"总请求数: {self.stats['total_requests']}")
        print(f"已确认数: {self.stats['confirmed']}")
        print(f"已完成数: {self.stats['completed']}")
        print(f"失败数: {self.stats['failed']}")
        print(f"总成交金额: {self.stats['total_traded_amount']:.2f}元")
        print("=" * 60)
    
    def get_statistics(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            Dict: 统计信息字典
        """
        with self.lock:
            return self.stats.copy()
    
    def get_trade_records(self) -> List[Dict]:
        """
        获取所有成交记录
        
        Returns:
            List[Dict]: 成交记录列表
        """
        with self.lock:
            all_trades = []
            for order_id, trades in self.trade_records.items():
                for trade in trades:
                    trade_copy = trade.copy()
                    trade_copy['order_id'] = order_id
                    all_trades.append(trade_copy)
            return all_trades
    
    def register_user_callback(self, event_type: str, callback_func):
        """
        注册用户自定义回调函数
        
        Args:
            event_type: 事件类型 ('on_order_confirmed', 'on_order_traded', 'on_order_completed', 'on_order_error')
            callback_func: 回调函数
        """
        if event_type in self.user_callbacks:
            self.user_callbacks[event_type].append(callback_func)
        else:
            print(f"[警告] 未知的事件类型: {event_type}")
    
    def _trigger_user_callback(self, event_type: str, data: Dict):
        """触发用户回调"""
        if event_type in self.user_callbacks:
            for callback in self.user_callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"[错误] 用户回调执行失败: {e}")
