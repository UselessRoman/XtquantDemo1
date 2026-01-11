# XTquant 量化交易框架

基于迅投量化（XTquant）的完整量化交易框架，包含数据管理、技术分析、策略开发、回测和实盘交易功能。

---

## 📑 目录

- [核心特性](#核心特性)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [功能模块详解](#功能模块详解)
- [使用示例](#使用示例)
- [API 接口说明](#api-接口说明)
- [配置说明](#配置说明)
- [测试指南](#测试指南)
- [开发指南](#开发指南)
- [版本管理与发布](#版本管理与发布)
- [版本历史](#版本历史)
- [注意事项](#注意事项)
- [贡献指南](#贡献指南)

---

## ✨ 核心特性

- 📊 **数据管理**：行情数据下载、财务数据获取、本地缓存
- 📈 **技术分析**：MA、MACD、KDJ 等技术指标计算和图表绘制
- 📉 **财务分析**：PE、PB、ROE 等财务指标评分
- 🎯 **智能选股**：基于技术+财务的多维度选股
- 🤖 **策略回测**：完整的回测引擎和性能分析
- 💹 **实盘交易**：异步交易、实时监控、自动交易
- 📡 **实时监控**：订单生命周期跟踪、成交记录、统计分析

---

## 🚀 快速开始

### 环境要求

1. **安装迅投 MiniQMT 客户端**：xtquant 需要连接 MiniQMT 客户端才能使用
2. **启动 MiniQMT**：运行代码前必须先启动 MiniQMT 客户端并登录
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

---

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
├── examples/                     # 示例代码目录
│   ├── main.py                   # QuantFramework 主类
│   ├── complete_example.py       # 完整功能示例（推荐）
│   ├── data_example.py           # 数据管理示例
│   ├── analysis_example.py       # 分析功能示例
│   ├── strategy_example.py       # 策略功能示例
│   ├── backtest_example.py       # 回测功能示例
│   ├── stock_selection_example.py # 选股功能示例
│   ├── trade_example.py          # 交易功能示例
│   ├── async_trade_monitor_example.py # 异步交易+监控示例
│   └── README.md                 # 示例说明文档
├── tests/                        # 测试代码
├── run_tests.py                  # 测试运行脚本
├── pytest.ini                    # Pytest配置
├── .coveragerc                   # 覆盖率配置
├── requirements.txt              # 依赖包列表
└── README.md                     # 本文件
```

---

## 📚 功能模块详解

### 1. 数据模块 (`src/data/`)

#### 1.1 行情数据管理

```python
from src.data.market_data import MarketDataManager

manager = MarketDataManager()

# 下载历史数据
manager.download_history_data('002352.SZ', '1d', '20240101', '20241231')

# 获取本地数据
data = manager.get_local_data('002352.SZ', '1d', '20240101', '20241231')

# 增量更新数据（自动从最后一条数据往后下载）
manager.update_data('002352.SZ', '1d')

# 批量下载
results = manager.batch_download(['002352.SZ', '000001.SZ'], '1d', '20240101', '20241231')
```

**注意**：xtquant 会自动管理数据存储，数据存储在 MiniQMT 安装目录下，无需手动指定路径。

#### 1.2 财务数据管理

```python
from src.data.financial_data import FinancialDataManager

manager = FinancialDataManager()

# 获取财务数据（如果本地没有会自动下载）
financial_data = manager.get_financial_data('002352.SZ', auto_download=True)

# 手动下载财务数据
manager.download_financial_data(['600000.SH', '000001.SZ'], 
                                 start_time='20200101', 
                                 end_time='20241231')

# 批量获取财务数据
all_data = manager.batch_get_financial_data(['002352.SZ', '000001.SZ'])
```

**财务数据字段说明**：
- 从 `Pershareindex` 表获取：ROE、EPS、BPS、营业收入增长率、净利润增长率、毛利率、净利率、资产负债率等
- 从 `Income` 表获取：营业收入、净利润、营业利润、利润总额等
- 从 `Balance` 表获取：总资产、总负债、股东权益等
- 从市场数据获取：PE、PB、市值（需要实时价格计算）

#### 1.3 财务数据接口详解

**三种财务数据函数的区别**：

| 函数 | 操作类型 | 数据来源 | 时间筛选 | 执行方式 |
|------|---------|---------|---------|---------|
| `get_financial_data()` | 读取 | 本地已下载数据 | ✅ 支持 | 立即返回 |
| `download_financial_data()` | 下载 | 服务器全部数据 | ❌ 不支持 | 同步阻塞 |
| `download_financial_data2()` | 下载 | 服务器指定范围 | ✅ 支持 | 同步阻塞 |

**推荐工作流程**：
```python
# 方式1：自动下载并获取（推荐）
data = manager.get_financial_data('600000.SH', auto_download=True)

# 方式2：手动下载后获取
manager.download_financial_data(['600000.SH'], start_time='20200101', end_time='20241231')
data = manager.get_financial_data('600000.SH', auto_download=False)
```

#### 1.4 行情数据使用指南

**订阅行情 vs 获取行情数据**：

- **订阅行情（Subscribe Quote）**：实时推送，事件驱动，适用于实时监控（本项目未实现）
- **获取行情数据（Get Market Data）**：主动获取，批量处理，适用于历史数据分析和回测（本项目使用）

**使用决策流程**：
```
需要数据 → 是否实时？
    │
    ├─ 是 → 是否需要持续监控？
    │      ├─ 是 → 使用 subscribe_quote()（未实现）
    │      └─ 否 → 使用 get_market_data()
    │
    └─ 否 → 是否需要历史数据？
             ├─ 是 → download_history_data() + get_local_data()
             └─ 否 → get_market_data()
```

---

### 2. 分析模块 (`src/analysis/`)

#### 2.1 技术指标分析

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

#### 2.2 财务指标分析

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

---

### 3. 策略模块 (`src/strategy/`)

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

---

### 4. 回测模块 (`src/backtest/`)

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

---

### 5. 选股模块 (`src/selection/`)

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

---

### 6. 交易模块 (`src/trading/`)

#### 6.1 基础交易接口

```python
from src.trading.trader import Trader

# 创建交易接口
trader = Trader(
    qmt_path=r'D:\qmt\...\userdata',  # QMT路径
    account_id='2000128'               # 账户ID
)

# 连接交易接口
trader.connect()

# 查询账户信息
account_info = trader.get_account_info()

# 查询持仓
positions = trader.get_positions()
```

#### 6.2 异步交易（推荐）

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

#### 6.3 实时监控

```python
from src.trading.trade_monitor import TradeMonitor

# 创建并注册监控器
monitor = TradeMonitor()
trader.trader.register_callback(monitor)

# 异步交易后，监控器自动跟踪所有订单
# 自动打印订单状态变化：
# [监控] 📋 委托回报: 买入600000.SH | 订单100001 | 状态:已报
# [监控] 💰 成交: 买入 600000.SH 10000股@10.50
# [监控] 📋 委托回报: 买入600000.SH | 订单100001 | 状态:已成

# 查看监控摘要
monitor.print_summary()

# 获取统计信息
stats = monitor.get_statistics()

# 查询订单状态
status = monitor.get_order_status(order_id)

# 获取成交记录
trades = monitor.get_trade_records()

# 导出数据
dataframes = monitor.export_to_dataframe()
```

#### 6.4 自动交易

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

#### 6.5 交易接口说明：同步、异步和回调

**同步（Synchronous）下单**：
- ⏱️ **阻塞式**：调用后程序暂停，等待结果
- ✅ **立即获得结果**：返回订单编号（order_id）
- ⚠️ **可能等待较久**：如果网络延迟或服务器处理慢，会阻塞程序

**异步（Asynchronous）下单（默认）**：
- ⚡ **非阻塞式**：调用后立即返回，不等待结果
- 📝 **返回请求序号**：返回 seq（序列号），用于追踪该请求
- 🔔 **通过回调获取结果**：实际的成功/失败通过回调函数通知
- 🚀 **高并发**：可以快速发送多个请求，不会阻塞

**回调（Callback）机制**：
- 🎯 **事件驱动**：当委托状态变化时自动触发
- 🔄 **实时通知**：委托回报、成交变动、错误等实时推送
- 📡 **被动接收**：不需要主动查询，系统主动推送

**主要回调事件**：
1. 委托回报回调 `on_stock_order`：委托状态变化时触发
2. 成交回报回调 `on_stock_trade`：有成交时触发
3. 异步下单响应回调 `on_order_stock_async_response`：异步下单的响应
4. 错误回调 `on_order_error`：下单失败时触发

**对比总结**：

| 特性 | 同步 | 异步（默认） | 回调 |
|------|------|------------|------|
| 执行方式 | 阻塞等待 | 立即返回 | 自动触发 |
| 返回值 | 订单编号 order_id | 请求序号 seq | 无返回值 |
| 结果获取 | 立即获得 | 通过回调获取 | 实时推送 |
| 性能 | 较慢（需等待） | 快（不等待） | 实时响应 |
| 适用场景 | 单笔交易 | 批量交易、高频 | 实时监控 |

#### 6.6 自定义回调

```python
# 注册自定义回调函数
def on_order_confirmed(data):
    print(f"订单确认: {data['order_id']}")

def on_order_traded(data):
    print(f"成交: {data['stock_code']} {data['volume']}股")

monitor.register_user_callback('on_order_confirmed', on_order_confirmed)
monitor.register_user_callback('on_order_traded', on_order_traded)
```

---

## 💡 使用示例

### 完整工作流程示例

#### 示例1：数据下载 → 分析 → 回测

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

#### 示例2：异步交易 + 实时监控

```python
from src.trading.trader import Trader
from src.trading.trade_monitor import TradeMonitor
import time

# 创建交易接口
trader = Trader(
    qmt_path=r'D:\qmt\投研\迅投极速交易终端睿智融科版\userdata',
    account_id='2000128'
)

# 创建并注册监控器
monitor = TradeMonitor()
trader.trader.register_callback(monitor)

trader.connect()

# 异步买入（自动监控）
seq1 = trader.buy('600000.SH', target_amount=10000)
seq2 = trader.buy('600519.SH', price=1800, quantity=1)

# 监控器自动跟踪所有订单状态
# 等待一段时间后查看摘要
time.sleep(5)
monitor.print_summary()
```

#### 示例3：选股 → 自动交易

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

### 示例文件说明

查看 `examples/` 目录获取更多详细示例：

- **`complete_example.py`** - 完整功能示例（推荐），包含所有核心功能的演示
- **`data_example.py`** - 数据管理功能示例
- **`analysis_example.py`** - 分析功能示例
- **`strategy_example.py`** - 策略功能示例
- **`backtest_example.py`** - 回测功能示例
- **`stock_selection_example.py`** - 选股功能示例
- **`trade_example.py`** - 交易功能示例
- **`async_trade_monitor_example.py`** - 异步交易+实时监控示例

**运行示例**：
```bash
# 运行完整功能示例
python examples/complete_example.py

# 运行特定功能示例
python examples/data_example.py
python examples/strategy_example.py
```

更多示例说明请参考 `examples/README.md`。

---

## ⚙️ API 接口说明

### QuantFramework 主类

`examples/main.py` 中的 `QuantFramework` 类整合了所有模块功能：

```python
from examples.main import QuantFramework

framework = QuantFramework(enable_trading=False, qmt_path=None, account_id=None)

# 数据管理
framework.download_data(stock_id, period, start_time, end_time)
framework.update_data(stock_id, period)
framework.get_data(stock_id, period, start_time, end_time)

# 分析功能
framework.analyze_data(stock_id, period, start_time, end_time, save_chart=True)

# 回测功能
framework.run_backtest(stock_id, strategy, period, start_time, end_time, save_chart=True)

# 选股功能
framework.select_stocks(financial_filters, technical_filters, min_total_score, max_results)

# 交易功能（需要 enable_trading=True）
framework.connect_trader()
framework.get_account_info()
framework.get_positions()
framework.buy_stock(stock_code, price, quantity)
framework.sell_stock(stock_code, price, quantity)
framework.run_auto_trading(stock_code, strategy, period, lookback_days)
```

---

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
- **注意**：xtquant 会自动管理数据存储，数据存储在 MiniQMT 安装目录下，不需要手动指定路径
- 默认时间参数：`DEFAULT_START_DATE`、`DEFAULT_PERIOD`

### TradeConfig - 交易配置
- **QMT_PATH**：QMT 客户端路径（需配置）
- **ACCOUNT_ID**：资金账号（需配置）
- **ACCOUNT_TYPE**：账户类型（'STOCK'/'CREDIT'/'FUTURE'）
- 风险控制参数（最大持仓比例、单股比例等）

**重要**：使用交易功能前，请在 `config.py` 中配置 `QMT_PATH` 和 `ACCOUNT_ID`，或在创建 `Trader` 时传入参数。

---

## 🧪 测试指南

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

---

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

monitor.register_user_callback('on_order_traded', my_custom_callback)
```

---

## 📦 版本管理与发布

### Git 配置

首次使用需要配置 Git 用户信息：

```bash
git config --global user.name "你的用户名"
git config --global user.email "你的邮箱@example.com"
```

### 上传项目到 GitHub

#### 步骤1：初始化 Git 仓库

```bash
cd e:\XTquantdemo1
git init
```

#### 步骤2：检查 .gitignore 文件

确保 `.gitignore` 文件包含以下内容：
- Python 缓存文件（`__pycache__/`, `*.pyc`）
- 虚拟环境（`.venv/`, `venv/`）
- IDE 配置（`.idea/`, `.vscode/`）
- 测试覆盖率报告（`htmlcov/`, `.pytest_cache/`）
- 日志文件（`*.log`）
- 系统文件（`.DS_Store`, `Thumbs.db`）

#### 步骤3：添加文件到 Git

```bash
# 查看要添加的文件（可选）
git status

# 添加所有文件到暂存区
git add .

# 创建首次提交
git commit -m "Initial commit: XTquant量化交易框架"
```

#### 步骤4：在 GitHub 上创建新仓库

1. 登录 GitHub (https://github.com)
2. 点击右上角的 "+" 号，选择 "New repository"
3. 填写仓库信息：
   - **Repository name**: `XTquant-demo`（或其他你喜欢的名字）
   - **Description**: `基于迅投量化(XTquant)的完整量化交易框架`
   - **Visibility**: 选择 Public（公开）或 Private（私有）
   - **不要**勾选 "Initialize this repository with a README"（因为本地已有文件）
4. 点击 "Create repository"

#### 步骤5：连接本地仓库到 GitHub

**使用 HTTPS（推荐，简单）**：

```bash
# 添加远程仓库（替换为你的实际仓库地址）
git remote add origin https://github.com/你的用户名/XTquant-demo.git

# 验证远程仓库
git remote -v
```

**使用 SSH（需要配置 SSH 密钥）**：

```bash
git remote add origin git@github.com:你的用户名/XTquant-demo.git
```

#### 步骤6：推送代码到 GitHub

```bash
# 推送代码（首次推送）
git branch -M main
git push -u origin main
```

### GitHub 认证说明

**重要：GitHub 不再支持密码认证，必须使用 Personal Access Token (PAT)**

#### 生成 Personal Access Token：

1. 登录 GitHub
2. 点击右上角头像 → **Settings**
3. 左侧菜单滚动到底部 → **Developer settings**
4. 点击 **Personal access tokens** → **Tokens (classic)**
5. 点击 **Generate new token (classic)**
6. 填写信息：
   - **Note**: `XTquant项目上传`（描述用途）
   - **Expiration**: 选择有效期（建议选择较长时间，如 90 天）
   - **勾选权限**: 至少勾选 `repo`（完整仓库权限）
7. 点击 **Generate token**
8. **立即复制 token**（格式类似：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）
   - ⚠️ **注意**：token 只会显示一次，请立即保存！

#### 使用 Token 推送代码：

```bash
# 推送时，系统会提示输入用户名和密码：
Username: 你的GitHub用户名
Password: 粘贴刚才复制的token（不是GitHub密码！）
```

#### 如果遇到 SSH 认证问题：

可以切换到 HTTPS：
```bash
git remote set-url origin https://github.com/你的用户名/仓库名.git
```

### 后续更新代码

当代码有更新时，使用以下命令：

```bash
# 查看更改
git status

# 添加更改的文件
git add .

# 提交更改
git commit -m "描述你的更改"

# 推送到 GitHub
git push
```

### 常用 Git 命令

```bash
# 查看当前状态
git status

# 查看提交历史
git log

# 查看远程仓库
git remote -v

# 查看分支
git branch

# 拉取远程更新
git pull

# 创建新分支
git checkout -b feature/新功能

# 切换分支
git checkout main
```

### 提交前检查清单

1. **不要提交敏感信息**：
   - API 密钥
   - 密码
   - 真实账户信息
   - 本地配置文件中的敏感数据

2. **.gitignore 已配置**：会自动排除：
   - `__pycache__/` - Python 缓存
   - `.venv/` - 虚拟环境
   - `.pytest_cache/` - 测试缓存
   - `htmlcov/` - 覆盖率报告
   - `*.log` - 日志文件
   - `.cursor/` - Cursor IDE 配置

3. **建议提交前检查**：
   ```bash
   git status
   git diff  # 查看具体更改内容
   ```

---

## ⚠️ 注意事项

1. **交易风险**：实盘交易前请充分测试，建议先在模拟环境验证
2. **数据依赖**：需要连接 MiniQMT 客户端，确保网络畅通
3. **账户配置**：交易功能需要配置正确的 QMT 路径和账户 ID
4. **异步监控**：使用异步交易时，监控器会自动跟踪订单状态，建议等待回调确认后再进行下一步操作
5. **数据存储**：xtquant 会自动管理数据存储，数据存储在 MiniQMT 安装目录下，无需手动管理
6. **数据更新**：行情数据使用 `incrementally=True` 自动增量更新，财务数据需要手动调用下载函数更新

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 贡献流程

1. Fork 本项目
2. 创建特性分支（`git checkout -b feature/新功能`）
3. 提交更改（`git commit -m "添加新功能"`）
4. 推送到分支（`git push origin feature/新功能`）
5. 提交 Pull Request

### 代码规范

- 遵循 PEP 8 Python 代码规范
- 添加适当的注释和文档字符串
- 为新功能添加测试用例
- 更新相关文档

---

## 📜 版本历史

### v2.0.0 (2026-01-07)

#### 重大更新
- ✅ 重构项目结构，实现模块化设计
- ✅ 整合所有文档到统一的 README.md
- ✅ 完善示例代码组织结构

#### 新增功能
- ✅ 异步交易和实时监控功能
- ✅ TradeMonitor 交易监控器
- ✅ 完整的示例文件体系（每种功能独立示例文件）

#### 改进
- ✅ 优化数据管理模块
- ✅ 完善财务数据接口使用
- ✅ 改进错误处理和提示信息

---

### v1.0.0 (2026-01-05)

#### 核心功能
- ✅ 选股模块：基于技术+财务的多维度选股
- ✅ 交易模块：同步/异步交易接口
- ✅ 自动交易模块：根据策略信号自动执行
- ✅ 测试框架：完整的 pytest 测试体系

#### 选股功能 (2026-01-05)
- ✅ 获取 A 股股票列表
- ✅ 获取财务数据（PE、PB、ROE、净利润增长率等）
- ✅ 计算技术指标得分（基于 MA、MACD、KDJ 等）
- ✅ 计算财务指标得分（基于 PE、PB、ROE 等）
- ✅ 综合选股（财务 60% + 技术 40%）
- ✅ 多种选股策略（价值投资、成长投资等）
- ✅ 选股结果保存

#### 交易功能 (2026-01-05)
- ✅ 交易接口连接和管理
- ✅ 查询账户信息和持仓
- ✅ 买入/卖出股票（支持限价单和市价单）
- ✅ 撤单功能
- ✅ 查询委托和成交记录
- ✅ 卖出全部持仓功能
- ✅ 根据策略信号自动执行交易
- ✅ 自动计算交易数量（根据可用资金）
- ✅ 持仓管理
- ✅ 交易历史记录

#### 测试功能 (2026-01-05)
- ✅ 完整的 pytest 测试框架
- ✅ 测试配置和 fixtures
- ✅ 样本数据生成器
- ✅ 工具函数测试
- ✅ 配置模块测试
- ✅ 数据分析模块测试
- ✅ 策略模块测试
- ✅ 回测模块测试
- ✅ 集成测试

#### 优化改进 (2026-01-05)
- ✅ 修正了 `download_history_data()` 的返回值处理
- ✅ 添加了数据下载后的验证机制
- ✅ 改进了数据清理逻辑
- ✅ 优化了索引转换（支持 YYYYMMDD 字符串格式和 DatetimeIndex）
- ✅ 添加了数据有效性检查
- ✅ 新增工具模块（日期格式化、股票代码验证等）
- ✅ 改进了错误处理

---

## 📄 许可证

本项目仅供学习和研究使用。

---

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送 Pull Request

---

**版本**: 2.0.0  
**最后更新**: 2026-01-07
