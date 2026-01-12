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
from src.selection.selector import MLStockSelector
from src.strategy.risk_control import RiskController
import pandas as pd
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
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
        
        if async_seq:
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


class MLAutoTrader(AutoTrader):
    """ML策略自动交易器：定时调仓+风控+再投资"""
    
    def __init__(self, trader: Trader = None, selector: MLStockSelector = None,
                 stock_num: int = 7):
        """
        初始化ML自动交易器
        
        Args:
            trader: 交易接口实例
            selector: ML选股器实例
            stock_num: 持仓股票数量
        """
        super().__init__(trader)  # 复用父类的交易接口和数据管理器
        self.selector = selector
        self.risk_controller = RiskController()
        self.stock_num = stock_num
        self.yesterday_limit_up_list = []  # 昨日涨停股票列表
        self.candidate_list = []  # 候选股列表（保存供再投资使用）
        self.candidate_scores = []  # 候选股得分（保存供再投资使用）
        self.prev_market_breadth = 20.0  # 默认市场宽度
        
    def rebalance_portfolio(self, target_stocks: List[str], scores: List[float],
                          end_date: str = None) -> Dict:
        """
        调仓逻辑：卖出不在目标列表的股票，买入新的股票（按得分分配资金）
        
        Args:
            target_stocks: 目标股票列表
            scores: 对应的模型得分列表
            end_date: 截止日期
            
        Returns:
            Dict: 调仓结果
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        print(f"\n{'=' * 60}")
        print(f"开始调仓 - {end_date}")
        print(f"{'=' * 60}")
        
        # 获取当前持仓
        positions_df = self.trader.get_positions()
        current_holdings = []
        if positions_df is not None and not positions_df.empty:
            current_holdings = positions_df['股票代码'].tolist()
        
        print(f"当前持仓: {current_holdings}")
        print(f"目标持仓: {target_stocks}")
        
        # 1. 卖出不在目标列表的股票（昨日涨停的除外）
        sold_stocks = []
        cash_released = 0.0
        
        for stock in current_holdings:
            if stock not in target_stocks and stock not in self.yesterday_limit_up_list:
                print(f"\n卖出: {stock}（不在目标列表中）")
                position = self.trader.get_position_by_code(stock)
                if position:
                    # 使用父类的卖出方法
                    async_seq = self._execute_sell(stock)
                    if async_seq:
                        # 估算释放的资金（使用持仓市值）
                        position_value = positions_df[positions_df['股票代码'] == stock]['持仓市值(元)'].iloc[0] if '持仓市值(元)' in positions_df.columns else 0
                        cash_released += position_value
                        sold_stocks.append(stock)
        
        # 2. 买入新的股票（按得分分配资金）
        if not target_stocks:
            print("\n[信息] 目标股票列表为空，不买入")
            return {'success': True, 'sold': sold_stocks, 'bought': []}
        
        # 检查市场宽度（市场弱势时清仓）
        market_breadth = self.risk_controller.calculate_market_breadth(end_date)
        if market_breadth < 45.0:
            print(f"\n[市场择时] 市场宽度: {market_breadth:.2f} < 45，清空所有持仓")
            # 清空所有持仓
            for stock in current_holdings:
                self._execute_sell(stock)
            return {'success': True, 'sold': current_holdings, 'bought': [], 'reason': 'market_weak'}
        
        # 保存候选股列表供再投资使用
        self.candidate_list = target_stocks
        self.candidate_scores = scores
        
        # 获取账户信息
        account_info = self.trader.get_account_info()
        if account_info is None:
            print("[错误] 无法获取账户信息")
            return {'success': False, 'message': '无法获取账户信息'}
        
        available_cash = account_info.get('可用资金', 0) + cash_released
        
        # 计算需要买入的股票（排除已持仓的）
        hold_stocks_updated = [s for s in current_holdings if s in target_stocks]
        stocks_to_buy = [s for s in target_stocks if s not in hold_stocks_updated]
        
        if not stocks_to_buy:
            print("\n[信息] 无需买入新股票")
            return {'success': True, 'sold': sold_stocks, 'bought': []}
        
        # 按得分分配资金
        bought_stocks = []
        stock_scores_dict = {stock: score for stock, score in zip(target_stocks, scores)}
        
        # 只对需要买入的股票按得分分配
        buy_scores = [stock_scores_dict[s] for s in stocks_to_buy]
        total_score = sum(buy_scores)
        
        if total_score == 0:
            # 如果得分全为0，平均分配
            avg_amount = available_cash / len(stocks_to_buy)
            for stock in stocks_to_buy:
                if len(bought_stocks) >= (self.stock_num - len(hold_stocks_updated)):
                    break
                async_seq = self._execute_buy_by_amount(stock, avg_amount, end_date)
                if async_seq:
                    bought_stocks.append(stock)
        else:
            # 按得分比例分配
            for stock in stocks_to_buy:
                if len(bought_stocks) >= (self.stock_num - len(hold_stocks_updated)):
                    break
                
                weight = stock_scores_dict[stock] / total_score
                invest_amount = available_cash * weight
                
                async_seq = self._execute_buy_by_amount(stock, invest_amount, end_date)
                if async_seq:
                    bought_stocks.append(stock)
        
        print(f"\n调仓完成:")
        print(f"  卖出: {len(sold_stocks)} 只")
        print(f"  买入: {len(bought_stocks)} 只")
        
        return {
            'success': True,
            'sold': sold_stocks,
            'bought': bought_stocks
        }
    
    def _execute_buy_by_amount(self, stock_code: str, target_amount: float, 
                               end_date: str = None) -> Optional[int]:
        """
        按目标金额买入股票
        
        Args:
            stock_code: 股票代码
            target_amount: 目标金额（元）
            end_date: 截止日期
            
        Returns:
            int: 异步下单序列号
        """
        try:
            # 获取当前价格
            if end_date:
                today = end_date
            else:
                today = datetime.now().strftime('%Y%m%d')
            
            data = self.data_manager.get_local_data(stock_code, '1d', today, today)
            if data is None or data.empty:
                # 尝试获取最新数据
                data = self.data_manager.get_local_data(stock_code, '1d')
            
            if data is None or data.empty:
                print(f"[警告] 无法获取 {stock_code} 的价格数据")
                return None
            
            current_price = data['close'].iloc[-1]
            
            # 计算最小金额（1手）
            min_amount = current_price * 100
            
            if target_amount < min_amount:
                print(f"[警告] {stock_code} 目标金额 {target_amount:.2f} 元不足1手（需要 {min_amount:.2f} 元）")
                return None
            
            # 执行买入
            async_seq = self.trader.buy(stock_code, target_amount=target_amount)
            return async_seq
            
        except Exception as e:
            print(f"[错误] 买入 {stock_code} 失败: {e}")
            return None
    
    def check_risk_control(self, end_date: str = None) -> Tuple[List[str], float]:
        """
        检查风控（ATR止损、RSRS风控）
        
        Args:
            end_date: 截止日期
            
        Returns:
            Tuple[List[str], float]: (触发风控的股票列表, 释放的现金总额)
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        positions_df = self.trader.get_positions()
        if positions_df is None or positions_df.empty:
            return [], 0.0
        
        triggered_stocks = []
        cash_released = 0.0
        
        # 获取当前价格数据
        for idx, row in positions_df.iterrows():
            stock_code = row['股票代码']
            
            # 豁免昨日涨停股票
            if stock_code in self.yesterday_limit_up_list:
                continue
            
            try:
                # 获取最新价格
                data = self.data_manager.get_local_data(stock_code, '1d', end_date, end_date)
                if data is None or data.empty:
                    data = self.data_manager.get_local_data(stock_code, '1d')
                
                if data is None or data.empty:
                    continue
                
                current_price = data['close'].iloc[-1]
                current_high = data['high'].iloc[-1] if len(data) > 0 else current_price
                position_cost = row.get('成本价', current_price)
                
                # 检查ATR止损
                triggered, stop_loss_level = self.risk_controller.check_stop_loss(
                    stock_code, current_price, position_cost, end_date
                )
                
                if triggered:
                    print(f"\n[ATR止损] {stock_code} 触发止损，现价: {current_price:.2f}, 止损位: {stop_loss_level:.2f}")
                    async_seq = self._execute_sell(stock_code)
                    if async_seq:
                        triggered_stocks.append(stock_code)
                        market_value = row.get('持仓市值(元)', 0)
                        cash_released += market_value
                        self.risk_controller.clear_stock_high(stock_code)
                    continue
                
                # 检查RSRS风控
                rsrs_value = self.risk_controller.calculate_rsrs(stock_code, end_date)
                if rsrs_value < -0.7:
                    print(f"\n[RSRS风控] {stock_code} RSRS值: {rsrs_value:.2f} < -0.7，卖出")
                    async_seq = self._execute_sell(stock_code)
                    if async_seq:
                        triggered_stocks.append(stock_code)
                        market_value = row.get('持仓市值(元)', 0)
                        cash_released += market_value
                    continue
                
                # 更新最高价记录
                self.risk_controller.update_stock_high(stock_code, current_high, position_cost)
                
            except Exception as e:
                print(f"[警告] 检查 {stock_code} 风控失败: {e}")
                continue
        
        # 触发风控后立即再投资
        if cash_released > 0 and self.check_market_timing(end_date):
            reinvested = self.reinvest(self.candidate_list, self.candidate_scores, cash_released, end_date)
            if reinvested:
                print(f"[风控再投资] 成功再投资 {len(reinvested)} 只股票")
        
        return triggered_stocks, cash_released
    
    def handle_limit_up_stocks(self, end_date: str = None) -> Tuple[List[str], float]:
        """
        处理涨停股票：昨日涨停继续持有，涨停打开则卖出
        
        Args:
            end_date: 截止日期
            
        Returns:
            Tuple[List[str], float]: (卖出的股票列表, 释放的现金)
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        positions_df = self.trader.get_positions()
        if positions_df is None or positions_df.empty:
            return [], 0.0
        
        sold_stocks = []
        cash_released = 0.0
        
        # 检查昨日涨停股票今日是否打开
        for stock_code in self.yesterday_limit_up_list[:]:
            if stock_code not in positions_df['股票代码'].tolist():
                self.yesterday_limit_up_list.remove(stock_code)
                continue
            
            try:
                # 获取最新价格数据
                data = self.data_manager.get_local_data(stock_code, '1d', end_date, end_date)
                if data is None or data.empty:
                    continue
                
                current_price = data['close'].iloc[-1]
                current_high = data['high'].iloc[-1]
                
                # 获取昨日数据判断昨日是否涨停
                yesterday = (datetime.strptime(end_date, '%Y%m%d') - timedelta(days=1)).strftime('%Y%m%d')
                yesterday_data = self.data_manager.get_local_data(stock_code, '1d', yesterday, yesterday)
                
                if yesterday_data is not None and not yesterday_data.empty:
                    prev_close = yesterday_data['close'].iloc[-1]
                    
                    # 判断涨停是否打开：当前价格 < 当前最高价，或涨幅<9.5%
                    if prev_close > 0:
                        pct_change = (current_price / prev_close - 1) * 100
                        # 如果涨停打开（价格不等于最高价，或涨幅小于9.5%）
                        if abs(current_price - current_high) > 0.01 or pct_change < 9.5:
                            print(f"[涨停打开] {stock_code} 涨停打开，卖出")
                            position = positions_df[positions_df['股票代码'] == stock_code].iloc[0]
                            market_value = position.get('持仓市值(元)', 0)
                            
                            async_seq = self._execute_sell(stock_code)
                            if async_seq:
                                sold_stocks.append(stock_code)
                                cash_released += market_value
                                self.yesterday_limit_up_list.remove(stock_code)
                                print(f"  释放资金: {market_value:.2f} 元")
                            else:
                                print(f"  卖出失败")
                        else:
                            print(f"[涨停继续] {stock_code} 继续涨停，持有")
                
            except Exception as e:
                print(f"[警告] 检查 {stock_code} 涨停状态失败: {e}")
        
        # 如果释放了资金，进行再投资
        if cash_released > 0 and self.check_market_timing(end_date):
            reinvested = self.reinvest(self.candidate_list, self.candidate_scores, cash_released, end_date)
            if reinvested:
                print(f"[再投资] 成功再投资 {len(reinvested)} 只股票")
        
        return sold_stocks, cash_released
    
    def update_limit_up_list(self, end_date: str = None):
        """
        更新昨日涨停股票列表
        
        Args:
            end_date: 截止日期
        """
        positions_df = self.trader.get_positions()
        if positions_df is None or positions_df.empty:
            self.yesterday_limit_up_list = []
            return
        
        # 获取昨日数据判断涨停
        if end_date is None:
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        else:
            yesterday = (datetime.strptime(end_date, '%Y%m%d') - timedelta(days=1)).strftime('%Y%m%d')
        
        limit_up_stocks = []
        for stock_code in positions_df['股票代码'].tolist():
            try:
                data = self.data_manager.get_local_data(stock_code, '1d', yesterday, yesterday)
                if data is None or data.empty:
                    continue
                
                # 判断是否涨停（收盘价接近最高价，且涨幅接近10%或20%）
                close_price = data['close'].iloc[-1]
                high_price = data['high'].iloc[-1]
                prev_close = data['close'].iloc[-2] if len(data) > 1 else close_price
                
                # 简单的涨停判断：收盘价等于最高价，且涨幅>9.5%
                if abs(close_price - high_price) < 0.01 and prev_close > 0:
                    pct_change = (close_price / prev_close - 1) * 100
                    if pct_change > 9.5:  # 接近涨停
                        limit_up_stocks.append(stock_code)
            except:
                continue
        
        self.yesterday_limit_up_list = limit_up_stocks
    
    def check_market_timing(self, end_date: str = None) -> bool:
        """
        检查市场择时（是否允许开仓）
        
        Args:
            end_date: 截止日期
            
        Returns:
            bool: True表示允许开仓，False表示禁止开仓
        """
        return self.risk_controller.check_market_timing(end_date)
    
    def reinvest(self, target_stocks: List[str], scores: List[float], 
                available_cash: float, end_date: str = None) -> List[str]:
        """
        再投资：将释放的资金按得分分配给新股票
        
        Args:
            target_stocks: 候选股票列表
            scores: 对应的模型得分
            available_cash: 可用现金
            end_date: 截止日期
            
        Returns:
            List[str]: 成功买入的股票列表
        """
        if not target_stocks or available_cash <= 0:
            return []
        
        # 获取当前持仓
        positions_df = self.trader.get_positions()
        current_holdings = []
        if positions_df is not None and not positions_df.empty:
            current_holdings = positions_df['股票代码'].tolist()
        
        # 排除已持仓的股票
        buy_candidates = [s for s in target_stocks if s not in current_holdings]
        if not buy_candidates:
            return []
        
        # 计算可用仓位
        available_slots = self.stock_num - len(current_holdings)
        if available_slots <= 0:
            return []
        
        # 按得分分配资金
        bought_stocks = []
        stock_scores_dict = {stock: score for stock, score in zip(target_stocks, scores)}
        
        buy_candidates = buy_candidates[:available_slots]
        candidate_scores = [stock_scores_dict[s] for s in buy_candidates]
        total_score = sum(candidate_scores)
        
        if total_score == 0:
            # 平均分配
            avg_amount = available_cash / len(buy_candidates)
            for stock in buy_candidates:
                async_seq = self._execute_buy_by_amount(stock, avg_amount, end_date)
                if async_seq:
                    bought_stocks.append(stock)
        else:
            # 按得分分配
            for stock in buy_candidates:
                weight = stock_scores_dict[stock] / total_score
                invest_amount = available_cash * weight
                async_seq = self._execute_buy_by_amount(stock, invest_amount, end_date)
                if async_seq:
                    bought_stocks.append(stock)
        
        return bought_stocks
