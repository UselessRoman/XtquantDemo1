# trade_monitor.py
"""
交易监控模块
功能：实时监控异步交易状态，管理订单生命周期
作者：WJC
日期：2026.1.5
"""

from xtquant.xttrader import XtQuantTraderCallback
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
            
            status_map = {
                0: '未报', 2: '已报', 3: '部成', 5: '已撤', 7: '已成', 8: '废单'
            }
            status_name = status_map.get(order_status, f'状态{order_status}')
            
            if order_id not in self.confirmed_orders:
                self.confirmed_orders[order_id] = {
                    'order_id': order_id,
                    'stock_code': stock_code,
                    'order_status': order_status,
                    'remark': order_remark,
                    'update_time': datetime.now(),
                }
                self.stats['confirmed'] += 1
            else:
                self.confirmed_orders[order_id]['order_status'] = order_status
                self.confirmed_orders[order_id]['update_time'] = datetime.now()
            
            print(f"[监控] 📋 委托回报: {order_remark} | 订单{order_id} | 状态:{status_name}")
            
            if order_status in [5, 7, 8]:
                self._mark_completed(order_id, status_name)
    
    def on_stock_trade(self, trade):
        """成交回报"""
        with self.lock:
            order_id = getattr(trade, 'order_id', '')
            stock_code = getattr(trade, 'stock_code', '')
            traded_price = getattr(trade, 'traded_price', 0)
            traded_volume = getattr(trade, 'traded_volume', 0)
            
            direction = '买入' if getattr(trade, 'offset_flag', '') == 48 else '卖出'
            amount = traded_price * traded_volume
            
            self.trade_records[order_id].append({
                'stock_code': stock_code,
                'direction': direction,
                'price': traded_price,
                'volume': traded_volume,
                'amount': amount,
            })
            self.stats['total_traded_amount'] += amount
            
            print(f"[监控] 💰 成交: {direction} {stock_code} {traded_volume}股@{traded_price:.2f}")
    
    def on_order_error(self, order_error):
        """委托失败"""
        with self.lock:
            error_msg = getattr(order_error, 'error_msg', '')
            self.error_records.append({'error_msg': error_msg, 'time': datetime.now()})
            self.stats['failed'] += 1
            print(f"[监控] ❌ 委托失败: {error_msg}")
    
    def _mark_completed(self, order_id: str, status: str):
        """标记订单完成"""
        if order_id in self.confirmed_orders:
            order = self.confirmed_orders[order_id]
            order['final_status'] = status
            self.completed_orders[order_id] = order
            self.stats['completed'] += 1
    
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
