# 克隆自聚宽文章：https://www.joinquant.com/post/65352
# 标题：机器学习多分类概率模型-年化112.5%-最大回撤11.6%
# 作者：zack2019

from jqdata import *
from jqfactor import *
import numpy as np
import pandas as pd
import pickle
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS


# 初始化函数
def initialize(context):
    # 设定基准
    set_benchmark('399101.XSHE')
    # 用真实价格交易
    set_option('use_real_price', True)
    # 打开防未来函数
    set_option("avoid_future_data", True)
    # 将滑点设置为0
    set_slippage(FixedSlippage(0))
    # 设置交易成本万分之三，不同滑点影响可在归因分析中查看
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0003, close_commission=0.0003,
                             close_today_commission=0, min_commission=5), type='stock')
    # 过滤order中低于error级别的日志
    log.set_level('order', 'error')
    # 初始化全局变量

    g.stock_num = 7
    g.hold_list = []  # 当前持仓的全部股票
    g.yesterday_HL_list = []  # 记录持仓中昨日涨停的股票

    g.model_small = pickle.loads(read_file('model_2024_multiclass.pkl'))
    
    g.candidate_list = []  # 当日候选股列表
    g.candidate_scores = []  # 候选股得分
    
    # 市场宽度相关全局变量
    g.prev_market_breadth = 20  # 默认市场宽度
    g.market_breadth_history = []  # 历史市场宽度

    # 因子列表
    g.factor_list = ['momentum', 'beta', 'sharpe_ratio_60', 'Variance120', 'natural_log_of_market_cap', 'boll_down', 'Rank1M', 'Variance20', 'MAWVAD', 'single_day_VPT_12', 'ARBR', 'cube_of_size', 'intangible_asset_ratio', 'Kurtosis120', 'DAVOL10', 'VR', 'sharpe_ratio_20', 'BBIC', 'operating_profit_to_total_profit', 'single_day_VPT', 'Volume1M', 'ATR6', 'book_to_price_ratio', 'Skewness20', 'VMACD', 'AR', 'Skewness120', 'VOL120', 'cash_flow_to_price_ratio', 'roa_ttm', 'arron_down_25', 'price_no_fq', 'net_operate_cash_flow_to_total_liability', 'Skewness60', 'TVMA6', 'Kurtosis60', 'non_recurring_gain_loss', 'MASS', 'earnings_yield', 'surplus_reserve_fund_per_share', 'earnings_to_price_ratio', 'growth', 'MFI14', 'Kurtosis20', 'net_operating_cash_flow_coverage', 'VOSC', 'VOL10', 'cash_earnings_to_price_ratio', 'total_operating_revenue_per_share', 'sales_to_price_ratio']
    #g.etf_pool = load_etf_pool()
    g.etf_pool = []
    g.m_days = 5 #动量参考天数
    #g.etf_info = initial_etf_info(g.etf_pool, 100)
    g.etf_info = []
    g.etf_pre = None
    
    g.atr_period = 14  # ATR计算周期
    g.atr_multiplier = 2  # ATR倍数[1,3](@ref)
    g.stock_highs = {}  # 记录持仓股票的最高价（用于跟踪止损）[4,6](@ref)

def after_code_changed(context):
    unschedule_all()
    # 市场宽度计算（收盘后）
    run_daily(calculate_market_breadth, time='15:30', reference_security='399101.XSHE')
 
    # 设置交易运行时间
    run_daily(prepare_stock_list, '9:15')
    # 改为半月调仓（每月1日和15日）
    #run_daily(sell, time='9:30')      # 分时段卖出
    
    run_monthly(weekly_adjustment, 1, '9:30')  # 1日调仓
    run_monthly(weekly_adjustment, 15, '9:30')  # 15日调仓
    
    
    run_daily(check_limit_up, '14:00') 
    run_weekly(check_dynamic_stoploss, 1, '9:30')
    run_weekly(check_individual_rsrs, 5,'14:30')  # 收盘前5分钟检查[1](@ref)
    run_daily(print_position_info,'15:30')
    
# ========== 原策略保留：市场宽度计算 ==========
def calculate_market_breadth(context):
    """计算当日市场宽度（中证全指成分股行业20日均线占比均值）000985.XSHG """
    try:
        stocks = get_index_stocks("399101.XSHE") 
        count = 20
        
        end_date = context.current_dt.strftime("%Y-%m-%d")
        h = get_price(
            stocks, end_date=end_date, frequency="1d", fields=["close"],
            count=count + 20, panel=False
        )
        
        h["date"] = pd.DatetimeIndex(h.time).date
        df_close = h.pivot(index="code", columns="date", values="close").dropna(axis=0)
        
        if df_close.shape[1] < 20:
            log.warning("数据不足20天，无法计算市场宽度")
            return
            
        df_ma20 = df_close.rolling(window=20, axis=1).mean().iloc[:, -1]
        df_bias = df_close.iloc[:, -1] > df_ma20
        
        def getStockIndustry(stocks):
            industry = get_industry(stocks)
            return pd.Series({
                stock: info.get("sw_l1", {}).get("industry_name", "Unknown")
                for stock, info in industry.items() if "sw_l1" in info
            })
        
        df_bias = pd.DataFrame({'code': df_bias.index, 'bias': df_bias.values})
        industry_data = getStockIndustry(stocks)
        df_bias['industry_name'] = df_bias['code'].map(industry_data)
        df_bias = df_bias[df_bias['industry_name'] != "Unknown"]
        
        industry_counts = df_bias.groupby('industry_name').count()
        industry_sums = df_bias.groupby('industry_name').sum()
        df_ratio = (industry_sums['bias'] * 100.0 / industry_counts['bias']).round()
        
        market_avg = df_ratio.mean()
        if pd.isna(market_avg):
            log.warning("市场宽度为NaN，使用前一日值")
            market_avg = g.prev_market_breadth
            
        g.prev_market_breadth = market_avg
        g.market_breadth_history.append(market_avg)
        log.info(f"当日市场平均宽度: {market_avg:.2f}")
        
    except Exception as e:
        log.error(f"计算市场宽度出错: {str(e)}")
        market_avg = g.prev_market_breadth
        g.market_breadth_history.append(market_avg)

def sell(context):
    """ST股分时段卖出逻辑"""
    # 市场择时：若市场弱势，直接清空持仓
    if g.prev_market_breadth < 45:
        for stock in list(context.portfolio.positions.keys()):
            order_target_value(stock, 0)
        log.info("市场弱势，清空所有持仓")
        return  
    
# 打印持仓信息
def print_position_info(context):
    position_percent = 100 * context.portfolio.positions_value /  context.portfolio.total_value
    # 打印账户信息
    for position in list(context.portfolio.positions.values()):
        securities=position.security
        cost=position.avg_cost
        price=position.price
        ret=100*(price/cost-1)
        value=position.value
        amount=position.total_amount
        hold_percent = 100 * value/context.portfolio.total_value
        print('代码:{}'.format(securities))
        print('成本价:{}'.format(format(cost,'.2f')))
        print('现价:{}'.format(price))
        print('收益率:{}%'.format(format(ret,'.2f')))
        print('持仓(股):{}'.format(amount))
        print('市值:{}'.format(format(value,'.2f')))
        print('持仓比例:{}%'.format(format(hold_percent,'.2f')))
        print('———————————————————————————————————')
    print('———————————————————————————————————————分割线————————————————————————————————————————')# 获取持仓信息
 
    
def check_dynamic_stoploss(context):
    """ATR动态跟踪止损"""
    now_time = context.current_dt
    cash_released = 0
    
    for stock, position in context.portfolio.positions.items():
        # 豁免ETF和涨停股
        if stock in g.yesterday_HL_list:
            continue
            
        # 获取最新价格数据[3,6](@ref)
        current_data = get_price(stock, end_date=context.previous_date, frequency='1m',
                                fields=['high', 'low', 'close'], count=1, 
                                skip_paused=True, fq='pre', panel=False)
        if current_data.empty:
            continue
            
        current_price = current_data.iloc[0]['close']
        current_high = current_data.iloc[0]['high']
        
        # 更新最高价记录[4,6](@ref)
        if stock not in g.stock_highs:
            g.stock_highs[stock] = position.avg_cost  # 初始化为成本价
        g.stock_highs[stock] = max(g.stock_highs[stock], current_high)
        
        # 计算ATR[3,4](@ref)
        atr_data = get_price(stock, end_date=context.previous_date, frequency='1d',
                            fields=['high', 'low', 'close'], 
                            count=g.atr_period + 1, skip_paused=True)
        if len(atr_data) < g.atr_period + 1:
            continue
            
        # 计算真实波幅(TR)[3,8](@ref)
        atr_data['prev_close'] = atr_data['close'].shift(1)
        atr_data['H-L'] = atr_data['high'] - atr_data['low']
        atr_data['H-PC'] = abs(atr_data['high'] - atr_data['prev_close'])
        atr_data['L-PC'] = abs(atr_data['low'] - atr_data['prev_close'])
        atr_data['TR'] = atr_data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        
        # 计算ATR[3,4](@ref)
        atr = atr_data['TR'].iloc[-g.atr_period:].mean()
        
        # 计算动态止损位[1,6](@ref)
        stop_loss_level = g.stock_highs[stock] - g.atr_multiplier * atr
        
        # 触发止损[4,8](@ref)
        if current_price <= stop_loss_level:
            if close_position(position):
                cash_released += position.value
                # 从最高价记录中移除[4](@ref)
                if stock in g.stock_highs:
                    del g.stock_highs[stock]
                log.info(f"ATR跟踪止损触发：{stock} 最高价:{g.stock_highs.get(stock,0):.2f} 止损位:{stop_loss_level:.2f} 现价:{current_price:.2f} ATR:{atr:.2f}")
  
    # 再投资逻辑保持不变
    if cash_released > 0:
        target_list, scores = get_stock_list(context)  # 获取最新候选股
        if not target_list:
            return
            
        # 排除已持仓且未触发RSRS的股票
        hold_stocks = [s.security for s in context.portfolio.positions.values()]
        buy_candidates = [s for s in target_list if s not in hold_stocks]
        
        # 计算可用仓位
        available_slots = g.stock_num - len(hold_stocks)
        if available_slots <= 0:
            return
        
        if buy_candidates:
            # 按模型得分分配资金
            candidate_scores = [scores[target_list.index(s)] for s in buy_candidates]
            total_score = sum(candidate_scores[:available_slots])
            for stock in buy_candidates[:available_slots]:
                weight = scores[target_list.index(stock)] / total_score
                invest_amount = cash_released * weight
                
                # 计算可投资金额（至少能买1手）
                price = get_price(stock, end_date=now_time, frequency='1m', 
                                fields='close', count=1).iloc[0, 0]
                min_amount = 100* price 
                
                if invest_amount >= min_amount:
                    if open_position(stock, invest_amount):
                        log.info(f"再投资 {stock} 金额: {invest_amount:.2f}")
  

def calculate_stock_rsrs(stock, end_date, n=18, m=600):
    # === 数据获取与清洗 ===
    data = get_price(stock, end_date=end_date, frequency='1d', 
                    fields=['high', 'low'], count=n + m, skip_paused=True)
    
    # 新增成交量加权
    volumes = get_price(stock, end_date=end_date, frequency='1d', 
                       fields=['volume'], count=n + m, skip_paused=True)['volume'].values
    
    # 数据不足检查
    if data is None or len(data) < n + m:
        return 0.0
        
    # 清洗无效值
    data.replace([np.inf, -np.inf], np.nan, inplace=True)
    data = data.dropna()
    if len(data) < n: 
        return 0.0
    
    # === 滑动窗口计算 ===
    highs = data['high'].values
    lows = data['low'].values
    betas = []
    r2_list = []
    
    for i in range(len(highs) - n + 1):
        window_highs = highs[i:i+n]
        window_lows = lows[i:i+n]
        
        # 窗口有效性检查
        if np.any(np.isnan(window_highs)) or np.any(np.isnan(window_lows)):
            continue
        if np.all(window_highs == window_highs[0]) or np.all(window_lows == window_lows[0]):
            continue
        
        X = sm.add_constant(window_lows)
        # 添加成交量权重
        weights = volumes[i:i+n] / np.sum(volumes[i:i+n])  # 归一化
        model = sm.WLS(window_highs, X, weights=weights)  # 替换OLS为WLS
        # model = sm.OLS(window_highs, X)
        result = model.fit()
        betas.append(result.params[1])
        r2_list.append(result.rsquared)
    
    # === 结果计算 ===
    if len(betas) == 0:
        return 0.0
        
    current_beta = betas[-1]
    current_r2 = r2_list[-1]
    
    # 动态调整窗口大小
    valid_m = min(m, len(betas))
    mu = np.mean(betas[-valid_m:])
    sigma = np.std(betas[-valid_m:])
    
    z_score = (current_beta - mu) / sigma if sigma != 0 else 0
    return z_score * current_r2 * current_beta
    
def check_individual_rsrs(context):
    """RSRS风控后立即再投资"""
    yesterday = context.previous_date
    cash_released = 0  # 记录释放的现金
    now_time = context.current_dt
    
    for stock in list(context.portfolio.positions):
        if stock[0] in ['1', '5']:  # 豁免ETF
            continue
        
        rsrs_value = calculate_stock_rsrs(stock, end_date=yesterday)
        
        if rsrs_value < -0.7 and stock not in g.yesterday_HL_list:
            # 记录释放的现金
            cash_released += context.portfolio.positions[stock].value
            close_position(context.portfolio.positions[stock])
            log.info(f"RSRS预警({rsrs_value:.2f})，清退: {stock}")
    
    if check_market_rsrs(context):  # 大盘弱势时跳过再投资
        return
    
    # 动态再投资（关键新增）
    if cash_released > 0:
        target_list, scores = get_stock_list(context)  # 获取最新候选股
        if not target_list:
            return
            
        # 排除已持仓且未触发RSRS的股票
        hold_stocks = [s.security for s in context.portfolio.positions.values()]
        buy_candidates = [s for s in target_list if s not in hold_stocks]
        
        # 计算可用仓位
        available_slots = g.stock_num - len(hold_stocks)
        if available_slots <= 0:
            log.info("持仓已达上限，跳过再投资")
            return
        
        if buy_candidates:
            # 按模型得分分配资金
            candidate_scores = [scores[target_list.index(s)] for s in buy_candidates]
            total_score = sum(candidate_scores[:available_slots])
            for stock in buy_candidates[:available_slots]:
                weight = scores[target_list.index(stock)] / total_score
                invest_amount = cash_released * weight
                
                # 计算可投资金额（至少能买1手）
                price = get_price(stock, end_date=now_time, frequency='1m', 
                                fields='close', count=1).iloc[0, 0]
                min_amount = 100* price 
                
                if invest_amount >= min_amount:
                    if open_position(stock, invest_amount):
                        log.info(f"再投资 {stock} 金额: {invest_amount:.2f}")
              
# 1-1 准备股票池
def prepare_stock_list(context):
    # 获取已持有列表
    g.hold_list = []
    for position in list(context.portfolio.positions.values()):
        stock = position.security
        g.hold_list.append(stock)
        
    # 获取昨日涨停列表
    if g.hold_list != []:
        df = get_price(g.hold_list, end_date=context.previous_date, frequency='daily', fields=['close', 'high_limit'],
                       count=1, panel=False, fill_paused=False)
        df = df[df['close'] == df['high_limit']]
        g.yesterday_HL_list = list(df.code)
    else:
        g.yesterday_HL_list = []
        
    # 保存候选股列表到全局变量
    g.candidate_list, g.candidate_scores = get_stock_list(context)


# 1-2 选股模块（优化版）
def get_stock_list(context):
    yesterday = context.previous_date
    stocks = get_index_stocks('399101.XSHE', yesterday)
    initial_list = filter_kcbj_stock(stocks)
    initial_list = filter_st_stock(initial_list)
    BIG_stock_list = get_fundamentals(query(
            valuation.code,
        ).filter(
            valuation.code.in_(initial_list),
            indicator.roe > 0.15,
            indicator.roa > 0.10,
        ).order_by(
    valuation.market_cap.asc()).limit(g.stock_num)).set_index('code').index.tolist()
    BIG_stock_list = filter_paused_stock(BIG_stock_list)
    BIG_stock_list = filter_new_stock(context, BIG_stock_list)
    BIG_stock_list = filter_limitup_stock(context,BIG_stock_list)
    BIG_stock_list = filter_limitdown_stock(context,BIG_stock_list)
    
    factor_data = get_factor_values(BIG_stock_list, g.factor_list, end_date=yesterday, count=1)
    df_jq_factor_value = pd.DataFrame(index=BIG_stock_list, columns=g.factor_list)
    
    for factor in g.factor_list:
        df_jq_factor_value[factor] = list(factor_data[factor].T.iloc[:, 0])
    
    # 获取模型预测得分
    tar = g.model_small.predict(df_jq_factor_value)
    print(len(tar[0]))
    # 使用原始类别作为权重计算 score
    # 可选：同时保存预测类别
    print(tar)
    
    df = df_jq_factor_value
    print("DataFrame columns:", df.columns.tolist())
    # 原始类别（必须和训练时 le.classes_ 一致！）
    classes_original = np.array([0,0.3,0.6,0.9,1.2,1.5,1.8,2.1])  # 类别2、5、9
    
    # 计算 score
    df['total_score'] = tar @ classes_original
    # 计算统计量
    mean_score = df['total_score'].mean()
    max_score = df['total_score'].max()
    median_score = df['total_score'].median()
    
    # 打印结果
    print(f"平均值 (Mean):    {mean_score:.4f}")
    print(f"最大值 (Max):     {max_score:.4f}")
    print(f"中位数 (Median):  {median_score:.4f}")
    # 关键优化：添加得分阈值过滤（>0.5）
    df = df[df['total_score'] > 0.61]  # 新增得分过滤条件
    """
    if df.empty:  # 处理无符合条件股票的情况
        
        sel_etf = get_rank(g.etf_pool)[0]
        hold_etf = None
        
        hold_worth = 0  # 默认认为持仓无价值
        # 卖出    
        hold_list = list(context.portfolio.positions)
        if len(hold_list)==1 and (hold_list[0][0] == '1' or hold_list[0][0] == '5'): 
            hold_etf = hold_list[0]
            hold_worth = evaluate_etf_worth(hold_etf, 1)
        sel_worth = evaluate_etf_worth(sel_etf, 0)
        
        # if(hold_etf != None):
        if sel_etf not in hold_list: #需要调仓，将选出的标的列入
            L = get_rank(g.etf_pool)[0:1]
        elif hold_worth==0: #需要空仓
            L = []
        else: #需要继续持有
            L = get_rank(g.etf_pool)[0:1]
        return L, [1.0]
        
    """
        
    
    df = df.sort_values(by=['total_score'], ascending=False)  
    lst = df.index.tolist()
    

    # 取前g.stock_num只，现在可能包含ETF
    lst = lst[:min(g.stock_num, len(lst))]
    
    # 为返回的候选列表构造得分列表
    # 首先获取股票部分的得分
    scores_list = list(df.loc[lst, 'total_score']) if not df.empty else []
    # 如果候选列表中包含ETF（即lst中的元素不在df.index中），则为其得分赋值
    # 注意：上面的判断逻辑可能将ETF加入lst，需要在这里处理
    final_scores = []
    for stock in lst:
        if stock in df.index:
            final_scores.append(df.loc[stock, 'total_score'])
        """
        else:
            # 这是ETF，使用之前设定的etf_score
            final_scores.append(etf_score) # 需要确保etf_score已定义
        """
    return lst, final_scores
    

def check_market_rsrs(context):
    """大盘择时阻止开仓"""
    market_rsrs = calculate_stock_rsrs('000300.XSHG', context.previous_date, n=18, m=200)
    if market_rsrs < -0.9:  # 沪深300弱势
        log.warning(f"大盘RSRS({market_rsrs:.2f})进入空头区域，禁止开仓")
        return True
    return False

# 1-3 整体调整持仓
def weekly_adjustment(context):
    now_time = context.current_dt
    # 市场择时：若市场弱势，直接清空持仓
    """
    if g.prev_market_breadth < 45:
        log.info("市场弱势，不买入")
        return
    """
    # 获取应买入列表及模型得分
    target_list, scores = get_stock_list(context)  # 修改1：同时获取模型得分
    
    # 调仓卖出（保持不变）
    for stock in g.hold_list:
        if (stock not in target_list) and (stock not in g.yesterday_HL_list):
            log.info("卖出[%s]" % (stock))
            position = context.portfolio.positions[stock]
            close_position(position)
        else:
            log.info("已持有[%s]" % (stock))
            
    # 动态资金分配（核心修改）
    position_count = len(context.portfolio.positions)
    target_num = len(target_list)
    
    if target_num > position_count:
        # 计算总得分和可用资金
        total_score = sum(scores)
        available_cash = context.portfolio.cash
        
        # 按模型得分动态分配资金
        for stock in target_list:
            if context.portfolio.positions[stock].total_amount == 0:
                # 计算该股票应分配的资金比例
                weight = scores[target_list.index(stock)] / total_score
                invest_amount = available_cash * weight  # 按权重分配资金
                
                # 计算可投资金额（至少能买1手）
                price = get_price(stock, end_date=now_time, frequency='1m', 
                                fields='close', count=1).iloc[0, 0]
                min_amount = 100*price
                
                if invest_amount >= min_amount:
                    if open_position(stock, invest_amount):
                        if len(context.portfolio.positions) == target_num:
                            break

def check_limit_up(context):
    now_time = context.current_dt
    cash_released = 0  # 记录释放的现金
    
    if g.yesterday_HL_list:
        # 对昨日涨停股票观察到尾盘如不涨停则卖出
        for stock in g.yesterday_HL_list:
            if stock not in context.portfolio.positions:
                continue
                
            current_data = get_price(stock, end_date=now_time, frequency='1m', 
                                    fields=['close', 'high_limit'], skip_paused=False, 
                                    fq='pre', count=1, panel=False, fill_paused=True)
            if current_data.empty:
                continue
                
            if current_data.iloc[0, 0] < current_data.iloc[0, 1]:  # 涨停打开
                log.info("[%s]涨停打开，卖出" % stock)
                position = context.portfolio.positions[stock]
                cash_released += position.value  # 记录释放的现金
                close_position(position)
            else:
                log.info("[%s]涨停，继续持有" % stock)
    
    # 关键优化：如果有资金释放，立即进行再投资
    if cash_released > 0 and not check_market_rsrs(context):
        # 获取最新候选股列表（排除已持仓且未触发RSRS的股票）
        hold_stocks = [s.security for s in context.portfolio.positions.values()]
        buy_candidates = [s for s in g.candidate_list if s not in hold_stocks]
        
        # 计算可用仓位
        available_slots = g.stock_num - len(hold_stocks)
        if available_slots <= 0 or not buy_candidates:
            return
        
        # 过滤当前不能买入的股票（涨停/跌停/停牌等）
        buy_candidates = filter_kcbj_stock(buy_candidates)
        buy_candidates = filter_st_stock(buy_candidates)
        buy_candidates = filter_paused_stock(buy_candidates)
        buy_candidates = filter_limitup_stock(context, buy_candidates)
        buy_candidates = filter_limitdown_stock(context, buy_candidates)
        
        if buy_candidates:
            # 按模型得分排序（高→低）
            candidate_scores = []
            for stock in buy_candidates[:available_slots]:
                if stock in g.candidate_list:
                    idx = g.candidate_list.index(stock)
                    candidate_scores.append((stock, g.candidate_scores[idx]))
            
            candidate_scores.sort(key=lambda x: x[1], reverse=True)
            total_score = sum(candi[1] for candi in candidate_scores)
            
            # 优先买入得分最高的股票
            for stock, score in candidate_scores:
                if cash_released <= 0:
                    break
                
                weight = score / total_score
                invest_amount = cash_released * weight
                
                # 计算可投资金额（至少能买1手）
                price = get_price(stock, end_date=now_time, frequency='1m', 
                                fields='close', count=1).iloc[0, 0]
                min_amount = 100* price
                
                if invest_amount >= min_amount:
                    if open_position(stock, invest_amount):
                        log.info(f"再投资 {stock} 金额: {invest_amount:.2f}")

# 3-1 交易模块-自定义下单
def order_target_value_(security, value):
    if value == 0:
        log.debug("Selling out %s" % (security))
    else:
        log.debug("Order %s to value %f" % (security, value))
    return order_target_value(security, value)


# 3-2 交易模块-开仓
def open_position(security, value):
    order = order_target_value_(security, value)
    if order != None and order.filled > 0:
        return True
    return False


# 3-3 交易模块-平仓
def close_position(position):
    security = position.security
    
    # 清除最高价记录
    if security in g.stock_highs:
        del g.stock_highs[security]
        
    order = order_target_value_(security, 0)  # 可能会因停牌失败
    if order != None:
        if order.status == OrderStatus.held and order.filled == order.amount:
            return True
    return False


# 2-1 过滤停牌股票
def filter_paused_stock(stock_list):
    current_data = get_current_data()
    return [stock for stock in stock_list if not current_data[stock].paused]


# 2-2 过滤ST及其他具有退市标签的股票
def filter_st_stock(stock_list):
    current_data = get_current_data()
    return [stock for stock in stock_list
            if not current_data[stock].is_st
            and 'ST' not in current_data[stock].name
            and '*' not in current_data[stock].name
            and '退' not in current_data[stock].name]


# 2-3 过滤科创北交股票
def filter_kcbj_stock(stock_list):
    for stock in stock_list[:]:
        if stock[0] == '4' or stock[0] == '8' or stock[:2] == '68' or stock[0] == '3':
            stock_list.remove(stock)
    return stock_list


# 2-4 过滤涨停的股票
def filter_limitup_stock(context, stock_list):
    last_prices = history(1, unit='1m', field='close', security_list=stock_list)
    current_data = get_current_data()
    return [stock for stock in stock_list if stock in context.portfolio.positions.keys()
            or last_prices[stock][-1] < current_data[stock].high_limit]


# 2-5 过滤跌停的股票
def filter_limitdown_stock(context, stock_list):
    last_prices = history(1, unit='1m', field='close', security_list=stock_list)
    current_data = get_current_data()
    return [stock for stock in stock_list if stock in context.portfolio.positions.keys()
            or last_prices[stock][-1] > current_data[stock].low_limit]


# 2-6 过滤次新股
def filter_new_stock(context, stock_list):
    yesterday = context.previous_date
    return [stock for stock in stock_list if
            not yesterday - get_security_info(stock).start_date < datetime.timedelta(days=375)]