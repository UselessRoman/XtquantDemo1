# config.py
"""
配置模块
功能：统一管理项目配置参数
作者：WJC
日期：2026.1.5
"""


class ChartConfig:
    """图表配置类"""
    # 颜色配置
    COLORS = {
        'up': '#E74C3C',  # 上涨红色
        'down': '#2ECC71',  # 下跌绿色
        'ma5': '#F39C12',  # MA5 橙色
        'ma10': '#3498DB',  # MA10 蓝色
        'ma20': '#9B59B6',  # MA20 紫色
        'dif': '#2980B9',  # DIF 深蓝
        'dea': '#E67E22',  # DEA 橙色
        'macd_positive': '#E74C3C',  # MACD正柱
        'macd_negative': '#2ECC71',  # MACD负柱
        'k': '#3498DB',  # K线蓝色
        'd': '#E67E22',  # D线橙色
        'j': '#9B59B6',  # J线紫色
        'grid': '#ECF0F1',  # 网格线
        'background': '#FFFFFF',  # 背景色
    }

    # 字体配置
    FONT_CONFIG = {
        'family': 'Arial, DejaVu Sans, sans-serif',
        'size_title': 14,
        'size_axis': 10,
        'size_tick': 9,
        'size_legend': 9,
    }

    # 布局配置
    LAYOUT = {
        'figsize': (16, 10),
        'panel_ratios': (4, 1, 1, 1),  # K线:成交量:MACD:KDJ
        'margin_left': 0.08,
        'margin_right': 0.95,
        'margin_bottom': 0.10,
        'margin_top': 0.92,
        'hspace': 0.15,
    }

    # 技术指标参数
    INDICATORS = {
        'ma_periods': [5, 10, 20],  # 均线周期
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'kdj_period': 9,
    }


class BacktestConfig:
    """回测配置类"""
    # 回测参数
    INITIAL_CAPITAL = 100000.0  # 初始资金
    COMMISSION_RATE = 0.0001  # 手续费率（万一）
    SLIPPAGE_RATE = 0.001  # 滑点率（0.1%）
    RISK_FREE_RATE = 0.03  # 无风险利率（年化3%）


class DataConfig:
    """数据配置类"""
    # 注意：xtquant会自动管理数据存储，数据存储在MiniQMT安装目录下
    # 不需要手动指定数据存储和缓存目录
    
    # 默认时间参数
    DEFAULT_START_DATE = '20240101'
    DEFAULT_PERIOD = '1d'  # 日线数据


class TradeConfig:
    """交易配置类"""
    # 交易接口路径（需要根据实际安装路径配置）
    # 券商端指定到 userdata_mini 文件夹
    # 投研端指定到 userdata 文件夹
    QMT_PATH = r'E:\国金QMT交易端模拟\userdata_mini'  # 留空则自动检测，或手动指定路径，如 r'D:\qmt\投研\迅投极速交易终端睿智融科版\userdata'
    
    # 账户配置
    ACCOUNT_ID = '8880835625'  # 资金账号，如 '2000128'
    ACCOUNT_TYPE = 'STOCK'  # 账户类型：'STOCK'股票账号, 'CREDIT'信用, 'FUTURE'期货
    
    # 交易参数
    DEFAULT_ORDER_TYPE = 0  # 默认订单类型：0=限价单，1=市价单
    MIN_ORDER_QUANTITY = 1  # 最小下单数量（手）
    MAX_ORDER_QUANTITY = 10000  # 最大下单数量（手）
    
    # 风险控制
    MAX_POSITION_RATIO = 0.8  # 最大持仓比例（80%）
    SINGLE_STOCK_RATIO = 0.3  # 单只股票最大持仓比例（30%）
    
    # 交易时间（简单判断，实际应使用交易日历）
    TRADING_START_TIME = '09:30'
    TRADING_END_TIME = '15:00'
    
    # 回调设置
    ENABLE_CALLBACK = True  # 是否启用回调
