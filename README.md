# XTquant 量化交易框架

基于迅投量化（XTquant）的完整量化交易框架，包含数据管理、技术分析、策略开发、回测和实盘交易功能。

## ✨ 核心特性

- 📊 **数据管理**：行情数据下载、财务数据获取、本地缓存
- 📈 **技术分析**：MA、MACD、KDJ等技术指标计算和图表绘制
- 📉 **财务分析**：PE、PB、ROE等财务指标评分
- 🎯 **智能选股**：基于技术+财务的多维度选股
- 🤖 **策略回测**：完整的回测引擎和性能分析
- 💹 **实盘交易**：异步交易、实时监控、自动交易
- 📡 **实时监控**：订单生命周期跟踪、成交记录、统计分析

## 🚀 快速开始

### 环境要求

1. **安装迅投MiniQMT客户端**：xtquant需要连接MiniQMT客户端才能使用
2. **启动MiniQMT**：运行代码前必须先启动MiniQMT客户端并登录
3. **Python 3.8+**

### 安装依赖

```bash
# 安装所有依赖
pip install -r requirements.txt

# 依赖包括：
# - xtquant（需要连接MiniQMT客户端）
# - pandas, numpy（数据处理）
# - matplotlib, mplfinance（图表绘制）
# - pytest, pytest-cov（测试工具）
```

### 基本使用

```python
from examples.main import QuantFramework
from src.strategy.strategies import MACDStrategy

# 创建框架实例
framework = QuantFramework()

# 下载历史数据
framework.download_data('002352.SZ', '1d', '20240101', '20241231')

# 运行策略回测
strategy = MACDStrategy()
result = framework.run_backtest('002352.SZ', strategy, '1d', '20240101', '20241231')
```

## 📁 项目结构

```
XTquantdemo1/
├── src/                          # 源代码目录
│   ├── data/                     # 数据模块
│   │   ├── market_data.py        # 行情数据管理
│   │   └── financial_data.py     # 财务数据管理
│   ├── analysis/                 # 分析模块
│   │   ├── technical.py          # 技术指标分析
│   │   └── fundamental.py        # 财务指标分析
│   ├── selection/                # 选股模块
│   │   └── selector.py           # 选股逻辑
│   ├── strategy/                 # 策略模块
│   │   └── strategies.py         # 交易策略（MACD、MA、KDJ等）
│   ├── backtest/                 # 回测模块
│   │   ├── engine.py             # 回测引擎
│   │   └── analyzer.py           # 性能分析器
│   ├── trading/                  # 交易模块
│   │   ├── trader.py             # 交易接口（同步/异步）
│   │   ├── auto_trader.py        # 自动交易器
│   │   └── trade_monitor.py      # 交易监控器（实时监控）
│   └── core/                     # 核心模块
│       ├── config.py             # 配置管理
│       └── utils.py              # 工具函数
├── examples/                     # 示例代码
│   ├── main.py                   # 框架主程序
│   ├── example.py                # 基本使用示例
│   ├── trade_example.py          # 交易功能示例
│   ├── async_trade_monitor_example.py # 异步交易+监控示例
│   └── stock_selection_example.py # 选股功能示例
├── tests/                        # 测试代码
├── run_tests.py                  # 测试运行脚本
├── pytest.ini                    # Pytest配置
├── .coveragerc                   # 覆盖率配置
└── requirements.txt              # 依赖包列表
```

## 📚 模块详细说明

### 数据模块 (`src/data/`)

#### 行情数据管理

```python
from src.data.market_data import MarketDataManager

manager = MarketDataManager()

# 下载历史数据
manager.download_history_data('002352.SZ', '1d', '20240101', '20241231')

# 获取本地数据
data = manager.get_local_data('002352.SZ', '1d', '20240101', '20241231')

# 增量更新数据（使用incrementally参数，自动从最后一条数据往后下载）
manager.update_data('002352.SZ', '1d')

# 批量下载
results = manager.batch_download(['002352.SZ', '000001.SZ'], '1d', '20240101', '20241231')
```

**注意**：xtquant会自动管理数据存储，数据存储在MiniQMT安装目录下，无需手动指定路径。

#### 财务数据管理

```python
from src.data.financial_data import FinancialDataManager

manager = FinancialDataManager()

# 获取财务数据（如果本地没有会自动下载）
financial_data = manager.get_financial_data('002352.SZ')

# 手动下载财务数据
manager.download_financial_data(['600000.SH', '000001.SZ'], start_time='20200101', end_time='20241231')

# 批量获取财务数据
all_data = manager.batch_get_financial_data(['002352.SZ', '000001.SZ'])
```

**财务数据字段说明**：
- 从 `Pershareindex` 表获取：ROE、EPS、BPS、营业收入增长率、净利润增长率、毛利率、净利率、资产负债率等
- 从 `Income` 表获取：营业收入、净利润、营业利润、利润总额等
- 从 `Balance` 表获取：总资产、总负债、股东权益等
- 从市场数据获取：PE、PB、市值（需要实时价格计算）

### 分析模块 (`src/analysis/`)

#### 技术指标分析

```python
from src.analysis.technical import TechnicalIndicators, ChartPlotter

calculator = TechnicalIndicators()

# 计算所有指标
indicators = calculator.calculate_all(data)
# 返回: {'ma': DataFrame, 'macd': DataFrame, 'kdj': DataFrame}

# 单独计算指标
ma_data = calculator.calculate_ma(data, periods=[5, 10, 20])
macd_data = calculator.calculate_macd(data)

# 绘制专业图表
plotter = ChartPlotter()
fig, axes = plotter.create_chart(data, indicators, '002352.SZ')
```

#### 财务指标分析

```python
from src.analysis.fundamental import FundamentalAnalyzer

analyzer = FundamentalAnalyzer()

# 计算财务得分（0-100分）
score_data = analyzer.calculate_financial_score(financial_data)
# 返回: {'score': 75, 'details': {...}}

# 财务数据筛选
filtered = analyzer.filter_financial_data(financial_data, {
    'max_pe': 30,
    'min_roe': 10
})
```

### 策略模块 (`src/strategy/`)

```python
from src.strategy.strategies import (
    Signal, SignalGenerator,
    MACDStrategy, MAStrategy, KDJStrategy, RSIStrategy,
    CombinedStrategy
)

# MACD策略
strategy = MACDStrategy()
signals = strategy.generate_signals(data, indicators)

# 均线策略
ma_strategy = MAStrategy(use_multiple_ma=True)

# 组合策略（多个策略投票）
combined = CombinedStrategy(
    strategies=[MACDStrategy(), MAStrategy(), KDJStrategy()],
    vote_threshold=2  # 至少2个策略同时发出信号
)
```

### 回测模块 (`src/backtest/`)

```python
from src.backtest.engine import BacktestEngine
from src.backtest.analyzer import PerformanceAnalyzer

# 创建回测引擎
engine = BacktestEngine(initial_capital=100000.0)

# 运行回测
result = engine.run(data, signals)

# 性能分析
analyzer = PerformanceAnalyzer()
performance = analyzer.analyze(result)
# 返回: {'总收益率': '15.5%', '年化收益率': '12.3%', '夏普比率': 1.2, ...}

# 绘制收益曲线
analyzer.plot_equity_curve(result)
```

### 选股模块 (`src/selection/`)

```python
from src.selection.selector import StockSelector

selector = StockSelector()

# 选股（综合技术和财务指标）
result = selector.select_stocks(
    financial_filters={
        'max_pe': 30,
        'min_roe': 10,
        'min_profit_growth': 5
    },
    technical_filters={
        'min_technical_score': 40,
        'require_above_ma20': True
    },
    min_total_score=60.0,
    max_results=20
)

# 保存选股结果
selector.save_selection_result(result, 'selected_stocks.csv')
```

### 交易模块 (`src/trading/`)

#### 基础交易接口

```python
from src.trading.trader import Trader

# 创建交易接口（自动启用监控）
trader = Trader(
    qmt_path=r'D:\qmt\...\userdata',  # QMT路径
    account_id='2000128',              # 账户ID
    use_monitor=True                   # 启用实时监控
)

# 连接交易接口
trader.connect()

# 查询账户信息
account_info = trader.get_account_info()

# 查询持仓
positions = trader.get_positions()
```

#### 异步交易（推荐）

```python
# 异步买入（默认，立即返回请求序号）
seq = trader.buy('600000.SH', target_amount=10000)  # 买入1万元
# 或指定数量
seq = trader.buy('600000.SH', price=10.5, quantity=10)  # 买入10手

# 异步卖出（默认，立即返回请求序号）
seq = trader.sell('600000.SZ', quantity=5)  # 卖出5手

# 卖出全部持仓
seq = trader.sell_all('600000.SH')

# 同步交易（阻塞等待结果）
order_id = trader.buy('600000.SH', price=10.5, quantity=10, async_mode=False)
```

#### 实时监控

```python
# 监控器自动跟踪所有异步订单
# 自动打印订单状态变化：
# [监控] 📋 委托回报: 买入600000.SH | 订单100001 | 状态:已报
# [监控] 💰 成交: 买入 600000.SH 10000股@10.50
# [监控] 📋 委托回报: 买入600000.SH | 订单100001 | 状态:已成

# 查看监控摘要
trader.monitor.print_summary()

# 获取统计信息
stats = trader.monitor.get_statistics()

# 查询订单状态
status = trader.monitor.get_order_status(order_id)

# 获取成交记录
trades = trader.monitor.get_trade_records()

# 导出数据
dataframes = trader.monitor.export_to_dataframe()
```

#### 自动交易

```python
from src.trading.auto_trader import AutoTrader
from src.strategy.strategies import MACDStrategy

# 创建自动交易器
auto_trader = AutoTrader(trader=trader)

# 运行策略并自动执行交易
strategy = MACDStrategy()
result = auto_trader.run_strategy(
    stock_code='002352.SZ',
    strategy=strategy,
    period='1d',
    lookback_days=100
)
# 返回: {'success': True, 'signal': 1, 'async_seq': 12345}
```

#### 自定义回调

```python
# 注册自定义回调函数
def on_order_confirmed(data):
    print(f"订单确认: {data['order_id']}")

def on_order_traded(data):
    print(f"成交: {data['stock_code']} {data['volume']}股")

trader.monitor.register_user_callback('on_order_confirmed', on_order_confirmed)
trader.monitor.register_user_callback('on_order_traded', on_order_traded)
```

## 📖 完整使用示例

### 示例1：数据下载 → 分析 → 回测

```python
from examples.main import QuantFramework
from src.strategy.strategies import MACDStrategy

framework = QuantFramework()

# 1. 下载数据
framework.download_data('002352.SZ', '1d', '20240101', '20241231')

# 2. 分析数据（计算指标并绘图）
framework.analyze_data('002352.SZ', '1d', '20240101', '20241231')

# 3. 运行回测
strategy = MACDStrategy()
result = framework.run_backtest('002352.SZ', strategy, '1d', '20240101', '20241231')

# 4. 查看回测结果
print(result['performance'])
```

### 示例2：异步交易 + 实时监控

```python
from src.trading.trader import Trader

# 创建交易接口（自动启用监控）
trader = Trader(
    qmt_path=r'D:\qmt\投研\迅投极速交易终端睿智融科版\userdata',
    account_id='2000128',
    use_monitor=True
)

trader.connect()

# 异步买入（自动监控）
seq1 = trader.buy('600000.SH', target_amount=10000)
seq2 = trader.buy('600519.SH', price=1800, quantity=1)

# 监控器自动跟踪所有订单状态
# 等待一段时间后查看摘要
import time
time.sleep(5)

trader.monitor.print_summary()
```

### 示例3：选股 → 自动交易

```python
from examples.main import QuantFramework
from src.strategy.strategies import MAStrategy

# 创建框架（启用交易）
framework = QuantFramework(enable_trading=True, 
                          qmt_path='...', 
                          account_id='2000128')
framework.connect_trader()

# 1. 选股
selected_stocks = framework.select_stocks(
    financial_filters={'max_pe': 30, 'min_roe': 10},
    max_results=5
)

# 2. 对选出的股票运行自动交易
strategy = MAStrategy()
for idx, row in selected_stocks.iterrows():
    stock_code = row['stock_code']
    framework.run_auto_trading(stock_code, strategy, lookback_days=100)
```

## 🔄 交易接口说明：同步、异步和回调

### 1. 同步（Synchronous）下单/撤单

**定义**：调用接口后，程序会**等待服务器响应**，直到收到结果才继续执行。

**特点**：
- ⏱️ **阻塞式**：调用后程序暂停，等待结果
- ✅ **立即获得结果**：返回订单编号（order_id）或成功/失败状态
- 🎯 **确定性**：调用完成后就知道是否成功
- ⚠️ **可能等待较久**：如果网络延迟或服务器处理慢，会阻塞程序

**适用场景**：
- 需要立即知道下单是否成功的场景
- 单笔交易操作，不需要高并发
- 程序逻辑需要等待交易结果才能继续

**示例**：
```python
# 同步下单：立即返回订单编号
order_id = trader.buy('600000.SH', price=10.5, quantity=10, async_mode=False)
# order_id > 0 表示成功，-1 表示失败

# 同步撤单：立即返回结果
result = trader.cancel_order(order_id, async_mode=False)
# result == True 表示成功
```

---

### 2. 异步（Asynchronous）下单/撤单

**定义**：调用接口后，程序**立即返回**一个请求序号（seq），不等待服务器响应，继续执行后续代码。

**特点**：
- ⚡ **非阻塞式**：调用后立即返回，不等待结果
- 📝 **返回请求序号**：返回 seq（序列号），用于追踪该请求
- 🔔 **通过回调获取结果**：实际的成功/失败通过回调函数通知
- 🚀 **高并发**：可以快速发送多个请求，不会阻塞

**适用场景**：
- 需要快速发送大量订单
- 程序需要继续执行其他逻辑，不能等待
- 高频交易场景
- 实时监控和响应场景

**示例**：
```python
# 异步下单：立即返回请求序号seq（默认模式）
seq = trader.buy('600000.SH', price=10.5, quantity=10)
# seq > 0 表示请求已提交，程序继续执行

# 异步撤单：立即返回请求序号seq
seq = trader.cancel_order(order_id, async_mode=True)
```

---

### 3. 回调（Callback）机制

**定义**：系统在特定事件发生时，**自动调用**你定义的函数来通知你。

**特点**：
- 🎯 **事件驱动**：当委托状态变化时自动触发
- 🔄 **实时通知**：委托回报、成交变动、错误等实时推送
- 📡 **被动接收**：不需要主动查询，系统主动推送

**主要回调事件**：
1. **委托回报回调** `on_stock_order`：委托状态变化时触发
2. **成交回报回调** `on_stock_trade`：有成交时触发
3. **异步下单响应回调** `on_order_stock_async_response`：异步下单的响应
4. **错误回调** `on_order_error`：下单失败时触发
5. **撤单错误回调** `on_cancel_error`：撤单失败时触发

**实现方式**：
- 通过 `TradeMonitor` 类自动接收和处理所有回调
- 可以注册自定义回调函数来扩展功能

---

### 对比总结

| 特性 | 同步 | 异步（默认） | 回调 |
|------|------|------------|------|
| **执行方式** | 阻塞等待 | 立即返回 | 自动触发 |
| **返回值** | 订单编号 order_id | 请求序号 seq | 无返回值 |
| **结果获取** | 立即获得 | 通过回调获取 | 实时推送 |
| **性能** | 较慢（需等待） | 快（不等待） | 实时响应 |
| **适用场景** | 单笔交易 | 批量交易、高频 | 实时监控 |
| **错误处理** | 直接判断返回值 | 通过回调判断 | 通过回调判断 |

---

### 项目中的实现

在 `trader.py` 中，默认使用**异步模式**：

```python
# 异步模式（默认）
seq = trader.buy('600000.SH', price=10.5, quantity=10)
# 返回请求序号 seq

# 同步模式
order_id = trader.buy('600000.SH', price=10.5, quantity=10, async_mode=False)
# 返回订单编号 order_id
```

**建议**：
- 对于大多数场景，使用**异步模式**（默认）性能更好
- 如果必须立即知道结果，使用**同步模式**
- 需要实时监控时，监控器会自动通过回调接收推送

---

## 📊 行情数据使用指南

### 订阅行情 vs 获取行情数据

#### 1. 订阅行情（Subscribe Quote）

**特点**：
- ✅ **实时推送**：数据会自动推送，无需主动查询
- ✅ **事件驱动**：通过回调函数接收数据更新
- ✅ **持续监控**：适用于实时监控多只股票
- ✅ **低延迟**：数据到达后立即触发回调

**适用场景**：
- 实时监控股票价格变化
- 实时交易决策（需要最新价格）
- 实时行情监控系统
- 高频策略执行

**本项目使用情况**：目前主要用于历史数据分析和策略回测，**未实现订阅行情功能**。如需实时交易，可考虑添加。

#### 2. 获取行情数据（Get Market Data）

**特点**：
- ✅ **主动获取**：需要主动调用API获取数据
- ✅ **批量处理**：适合批量获取多只股票数据
- ✅ **历史数据**：可以获取历史K线数据
- ✅ **一次性返回**：调用后立即返回结果

**适用场景**：
- 历史数据分析
- 策略回测
- 批量选股
- 技术指标计算
- 一次性数据查询

**本项目实现**：
- ✅ `MarketDataManager.download_history_data()` - 下载历史数据
- ✅ `MarketDataManager.get_local_data()` - 获取本地已下载数据
- ✅ `MarketDataManager.update_data()` - 增量更新数据（使用 `incrementally=True`）

#### 使用决策流程

```
需要数据 → 是否实时？
    │
    ├─ 是 → 是否需要持续监控？
    │      │
    │      ├─ 是 → 使用 subscribe_quote() 订阅行情（未实现）
    │      │
    │      └─ 否 → 使用 get_market_data() 获取快照
    │
    └─ 否 → 是否需要历史数据？
             │
             ├─ 是 → 先 download_history_data() 下载
             │       再 get_local_data() 获取
             │
             └─ 否 → 使用 get_market_data() 获取当前数据
```

---

## 💰 财务数据接口说明

### 三种财务数据函数的区别

xtquant 提供了三种财务数据相关的函数：

#### 1. `get_financial_data()` - 获取财务数据（从本地读取）

**作用**：从**本地已下载**的财务数据中读取数据，**不会**从服务器下载新数据。

**特点**：
- ✅ **只读操作**：不下载数据，仅读取本地数据
- ✅ **速度快**：本地读取，无需网络请求
- ✅ **支持时间筛选**：可以指定 `start_time` 和 `end_time`
- ✅ **支持报表筛选**：可以选择按截止日期或披露日期筛选
- ❌ **依赖本地数据**：如果本地没有数据，返回空结果

**使用场景**：
- 已经下载过数据，需要读取和分析
- 快速查询已有的财务数据
- 不需要更新数据时

#### 2. `download_financial_data()` - 下载财务数据（简单版）

**作用**：从服务器下载财务数据到本地，**同步执行**，下载完成后才返回。

**特点**：
- ✅ **下载操作**：从服务器下载数据到本地
- ✅ **简单易用**：不需要指定时间范围，下载全部可用数据
- ✅ **同步执行**：阻塞式，下载完成后才返回
- ❌ **无时间控制**：无法指定下载的时间范围

**使用场景**：
- 首次下载数据，需要全部历史数据
- 不需要时间范围控制时

#### 3. `download_financial_data2()` - 下载财务数据（高级版）

**作用**：从服务器下载财务数据到本地，支持时间范围筛选。

**特点**：
- ✅ **下载操作**：从服务器下载数据到本地
- ✅ **时间控制**：可以指定 `start_time` 和 `end_time`（按披露日期筛选）
- ✅ **同步执行**：阻塞式，下载完成后才返回

**使用场景**：
- 需要下载指定时间范围的数据
- 需要增量更新数据时

### 对比总结

| 特性 | `get_financial_data()` | `download_financial_data()` | `download_financial_data2()` |
|------|------------------------|----------------------------|------------------------------|
| **操作类型** | 读取（从本地） | 下载（从服务器） | 下载（从服务器） |
| **是否需要网络** | ❌ 否 | ✅ 是 | ✅ 是 |
| **时间范围筛选** | ✅ 支持 | ❌ 不支持 | ✅ 支持 |
| **执行方式** | 立即返回 | 同步（阻塞） | 同步（阻塞） |
| **数据来源** | 本地已下载数据 | 服务器全部数据 | 服务器指定范围数据 |
| **适用场景** | 读取已下载数据 | 首次下载全部数据 | 批量/增量下载 |

### 推荐工作流程

**方式1：自动下载并获取（推荐）**
```python
manager = FinancialDataManager()

# 自动判断：如果本地没有数据则自动下载
data = manager.get_financial_data('600000.SH', auto_download=True)
```

**方式2：手动下载后获取**
```python
# 1. 先下载数据
manager.download_financial_data(
    stock_list=['600000.SH'],
    start_time='20200101',
    end_time='20241231'
)

# 2. 然后获取数据
data = manager.get_financial_data('600000.SH', auto_download=False)
```

**注意**：
- 下载的数据会自动存储在 MiniQMT 安装目录下，无需手动管理
- `download_financial_data2()` 的 `start_time` 和 `end_time` 是按**披露日期**（`m_anntime`）筛选的

---

## 🧪 运行测试

### 方式1：使用 run_tests.py（推荐）

```bash
# 运行所有测试
python run_tests.py

# 运行单元测试
python run_tests.py --type unit

# 运行集成测试
python run_tests.py --type integration

# 快速测试
python run_tests.py --type quick

# 不生成覆盖率报告
python run_tests.py --no-coverage
```

### 方式2：直接使用 pytest

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_strategies.py

# 显示详细输出
pytest -v

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

### 方式3：在 Cursor IDE 中运行

1. 打开测试文件（如 `tests/test_strategies.py`）
2. 点击测试函数或测试类上方的运行按钮 ▶️
3. 或右键点击选择 "Run Test"

**启用测试运行器**：
- 确保 `.vscode/settings.json` 中 `python.testing.pytestEnabled: true`
- 按 `Ctrl + Shift + P` → 输入 "Test: Focus on Test View" 打开测试资源管理器

### 测试覆盖率

```bash
# 生成覆盖率报告
pytest --cov=src --cov-report=html

# 查看报告（浏览器打开）
start htmlcov/index.html  # Windows
```

## 📝 配置说明

配置文件位于 `src/core/config.py`：

### ChartConfig - 图表配置
- 颜色、字体、布局设置
- 技术指标参数（MA周期、MACD参数等）

### BacktestConfig - 回测配置
- 初始资金：`INITIAL_CAPITAL = 100000.0`
- 手续费率：`COMMISSION_RATE = 0.0001`（万1）
- 滑点率：`SLIPPAGE_RATE = 0.001`（0.1%）

### DataConfig - 数据配置
- **注意**：xtquant会自动管理数据存储，数据存储在MiniQMT安装目录下，不需要手动指定路径
- 默认时间参数：`DEFAULT_START_DATE`、`DEFAULT_PERIOD`

### TradeConfig - 交易配置
- **QMT_PATH**：QMT客户端路径（需配置）
- **ACCOUNT_ID**：资金账号（需配置）
- **ACCOUNT_TYPE**：账户类型（'STOCK'/'CREDIT'/'FUTURE'）
- 风险控制参数（最大持仓比例、单股比例等）

**重要**：使用交易功能前，请在 `config.py` 中配置 `QMT_PATH` 和 `ACCOUNT_ID`，或在创建 `Trader` 时传入参数。

## 🔧 开发指南

### 添加新策略

在 `src/strategy/strategies.py` 中继承 `SignalGenerator` 类：

```python
class MyStrategy(SignalGenerator):
    def generate_signals(self, data, indicators):
        signals = []
        # 实现策略逻辑
        # 返回 Signal 对象列表
        return signals
```

### 添加新指标

在 `src/analysis/technical.py` 中的 `TechnicalIndicators` 类添加方法：

```python
def calculate_my_indicator(self, data, period=14):
    # 计算指标
    result = pd.Series(...)
    return result
```

### 添加新监控回调

```python
def my_custom_callback(data):
    # 处理回调数据
    pass

trader.monitor.register_user_callback('on_order_traded', my_custom_callback)
```

## 🔍 更多示例

查看 `examples/` 目录获取更多示例：

- `examples/example.py` - 基本使用示例（数据、分析、回测）
- `examples/trade_example.py` - 交易功能示例（买卖、持仓管理）
- `examples/async_trade_monitor_example.py` - 异步交易+实时监控示例
- `examples/stock_selection_example.py` - 选股功能示例
- `examples/main.py` - 完整框架集成示例

## ⚠️ 注意事项

1. **交易风险**：实盘交易前请充分测试，建议先在模拟环境验证
2. **数据依赖**：需要连接MiniQMT客户端，确保网络畅通
3. **账户配置**：交易功能需要配置正确的QMT路径和账户ID
4. **异步监控**：使用异步交易时，监控器会自动跟踪订单状态，建议等待回调确认后再进行下一步操作
5. **数据存储**：xtquant会自动管理数据存储，数据存储在MiniQMT安装目录下，无需手动管理
6. **数据更新**：行情数据使用 `incrementally=True` 自动增量更新，财务数据需要手动调用下载函数更新

## 📄 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**版本**: 2.0.0  
**最后更新**: 2026-01-07
