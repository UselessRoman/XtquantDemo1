# auto_trader.py
"""
自动交易模块
功能：将策略信号转换为实际交易
作者：WJC
日期：2026.1.5
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.trading.trader import Trader
from src.strategy.strategies import Signal, SignalGenerator
from src.data.market_data import MarketDataManager
from src.analysis.technical import TechnicalIndicators
import pandas as pd
from typing import Dict, Optional
from datetime import datetime
from src.core.config import TradeConfig
from src.core.utils import validate_stock_code


class AutoTrader:
    """自动交易器：根据策略信号自动执行交易"""
    
    def __init__(self, trader: Trader = None):
        """
        初始化自动交易器
        
        Args:
            trader: 交易接口实例，如果为None则自动创建
        """
        self.trader = trader or Trader()
        self.data_manager = MarketDataManager()
        self.indicator_calculator = TechnicalIndicators()
        self.trade_history = []  # 交易历史记录
    
    def connect(self) -> bool:
        """连接交易接口"""
        return self.trader.connect()
    
    def execute_signal(self, stock_code: str, signal: int, 
                      current_price: float = None,
                      quantity: int = None) -> Optional[int]:
        """
        执行交易信号
        
        Args:
            stock_code: 股票代码
            signal: 交易信号，1=买入，-1=卖出，0=持有
            current_price: 当前价格，如果为None则使用市价
            quantity: 交易数量（手），如果为None则根据资金自动计算
            
        Returns:
            int: 异步下单序列号，失败返回None
        """
        if signal == Signal.BUY.value:
            return self._execute_buy(stock_code, current_price, quantity)
        elif signal == Signal.SELL.value:
            return self._execute_sell(stock_code, current_price, quantity)
        else:
            return None
    
    def _execute_buy(self, stock_code: str, price: float = None,
                     quantity: int = None) -> Optional[str]:
        """执行买入"""
        # 获取账户信息
        account_info = self.trader.get_account_info()
        if account_info is None:
            print("[错误] 无法获取账户信息，买入失败")
            return None
        
        # 获取可用资金
        available_cash = 0
        if '可用资金' in account_info:
            available_cash = account_info['可用资金']
        elif 'availableCash' in account_info:
            available_cash = account_info['availableCash']
        elif '可用余额' in account_info:
            available_cash = account_info['可用余额']
        
        if available_cash <= 0:
            print("[错误] 账户可用资金不足")
            return None
        
        # 如果没有指定数量，根据资金计算目标金额
        if quantity is None:
            # 使用可用资金的80%买入
            target_amount = available_cash * TradeConfig.MAX_POSITION_RATIO
            # 执行买入（按目标金额）
            async_seq = self.trader.buy(
                stock_code, 
                price=price if price and price > 0 else 0,
                target_amount=target_amount
            )
        else:
            # 限制数量
            quantity = max(TradeConfig.MIN_ORDER_QUANTITY, 
                          min(quantity, TradeConfig.MAX_ORDER_QUANTITY))
            # 执行买入（按数量）
            async_seq = self.trader.buy(stock_code, price, quantity)
        
        if async_seq:
            self.trade_history.append({
                'time': datetime.now(),
                'action': 'BUY',
                'stock_code': stock_code,
                'price': price,
                'quantity': quantity,
                'async_seq': async_seq
            })
        
        return async_seq
    
    def _execute_sell(self, stock_code: str, price: float = None,
                     quantity: int = None) -> Optional[str]:
        """执行卖出"""
        # 查询持仓
        position = self.trader.get_position_by_code(stock_code)
        
        if position is None:
            print(f"[错误] 未持有股票 {stock_code}，无法卖出")
            return None
        
        # 获取可用持仓数量
        available_quantity = 0
        if 'canUseVol' in position:
            available_quantity = position['canUseVol'] // 100  # 转换为手
        elif '可用数量' in position:
            available_quantity = position['可用数量'] // 100
        
        if available_quantity <= 0:
            print(f"[错误] 股票 {stock_code} 无可用持仓")
            return None
        
        # 如果没有指定数量，卖出全部可用持仓
        if quantity is None:
            quantity = available_quantity
        else:
            quantity = min(quantity, available_quantity)
        
        # 执行卖出
        async_seq = self.trader.sell(
            stock_code, 
            price=price if price and price > 0 else 0,
            quantity=quantity
        )
        
        if order_id:
            self.trade_history.append({
                'time': datetime.now(),
                'action': 'SELL',
                'stock_code': stock_code,
                'price': price,
                'quantity': quantity,
                'async_seq': async_seq
            })
        
        return async_seq
    
    def run_strategy(self, stock_code: str, strategy: SignalGenerator,
                    period: str = "1d", lookback_days: int = 100) -> Dict:
        """
        运行策略并执行交易
        
        Args:
            stock_code: 股票代码
            strategy: 交易策略
            period: 数据周期
            lookback_days: 回看天数
            
        Returns:
            Dict: 执行结果
        """
        print(f"\n{'=' * 60}")
        print(f"运行策略自动交易: {stock_code}")
        print(f"策略: {strategy.__class__.__name__}")
        print(f"{'=' * 60}")
        
        # 获取数据
        from datetime import timedelta
        end_time = datetime.now().strftime('%Y%m%d')
        start_time = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y%m%d')
        
        data = self.data_manager.get_local_data(stock_code, period, start_time, end_time)
        
        if data is None or data.empty:
            print("[错误] 无法获取数据")
            return {'success': False, 'message': '无法获取数据'}
        
        # 计算技术指标
        indicators = self.indicator_calculator.calculate_all(data)
        
        # 生成交易信号
        signals = strategy.generate_signals(data, indicators)
        
        # 获取最新信号
        latest_signal = signals.iloc[-1]
        latest_price = data['close'].iloc[-1]
        
        print(f"\n最新信号: {latest_signal} ({'买入' if latest_signal == 1 else '卖出' if latest_signal == -1 else '持有'})")
        print(f"最新价格: {latest_price:.2f}")
        
        # 执行交易
        if latest_signal != Signal.HOLD.value:
            order_id = self.execute_signal(stock_code, latest_signal, latest_price)
            
            if order_id:
                return {
                    'success': True,
                    'signal': latest_signal,
                    'price': latest_price,
                    'order_id': order_id
                }
            else:
                return {
                    'success': False,
                    'message': '交易执行失败'
                }
        else:
            print("当前信号为持有，不执行交易")
            return {
                'success': True,
                'signal': latest_signal,
                'message': '持有信号，未执行交易'
            }
    
    def get_trade_history(self) -> pd.DataFrame:
        """获取交易历史"""
        if self.trade_history:
            return pd.DataFrame(self.trade_history)
        else:
            return pd.DataFrame()
    
    def clear_trade_history(self):
        """清空交易历史"""
        self.trade_history = []
