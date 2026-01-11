# 示例文件说明

> 📖 **完整文档**：请查看项目根目录的 [README.md](../README.md) 获取完整的项目文档。

本目录包含框架的各种使用示例，展示不同功能的使用方法。

## 📁 示例文件列表

### 核心文件

#### `main.py` - QuantFramework 主类
**框架核心类文件**，包含 `QuantFramework` 类的完整定义，整合了所有模块功能。

**不包含示例代码**，只作为类定义使用。

---

### 功能示例文件

#### 1. `data_example.py` - 数据管理示例
**展示数据管理功能**：

- 行情数据管理（下载、获取、更新、批量操作）
- 财务数据管理（获取、批量获取、下载）

**运行方式**：
```bash
python examples/data_example.py
```

---

#### 2. `analysis_example.py` - 分析功能示例
**展示分析功能**：

- 技术指标分析（MA、MACD、KDJ计算、图表绘制）
- 财务指标分析（得分计算、数据筛选）

**运行方式**：
```bash
python examples/analysis_example.py
```

---

#### 3. `strategy_example.py` - 策略功能示例
**展示交易策略功能**：

- 单个策略使用（MACD、MA、KDJ）
- 组合策略
- 策略对比

**运行方式**：
```bash
python examples/strategy_example.py
```

---

#### 4. `backtest_example.py` - 回测功能示例
**展示策略回测功能**：

- 单个策略回测
- 多策略回测对比
- 组合策略回测

**运行方式**：
```bash
python examples/backtest_example.py
```

---

#### 5. `stock_selection_example.py` - 选股功能示例
**展示选股功能**：

- 基础选股
- 价值投资选股
- 成长投资选股
- 自定义股票列表选股
- 详细分析单只股票

**运行方式**：
```bash
python examples/stock_selection_example.py
```

---

#### 6. `trade_example.py` - 交易功能示例
**展示交易相关功能**：

- 基本交易操作（查询账户、持仓、买入、卖出、撤单）
- 自动交易（根据策略信号自动执行）
- 使用完整框架进行交易
- 持仓管理

**注意事项**：
- ⚠️ 涉及实盘交易，请谨慎操作
- 需要连接 MiniQMT 客户端
- 建议先在模拟环境测试

**运行方式**：
```bash
python examples/trade_example.py
```

---

#### 7. `async_trade_monitor_example.py` - 异步交易+实时监控示例
**展示异步交易和实时监控功能**：

- 异步交易+自动监控
- 注册自定义回调函数
- 批量异步交易

**运行方式**：
```bash
python examples/async_trade_monitor_example.py
```

---

### 整体示例文件

#### 8. `complete_example.py` - 完整功能示例（推荐）
**功能最全面的示例文件**，包含所有核心功能的演示：

- ✅ 行情数据管理（下载、获取、更新、批量操作）
- ✅ 财务数据管理（获取、批量获取）
- ✅ 技术指标分析（MA、MACD、KDJ计算、图表绘制）
- ✅ 财务指标分析（得分计算、数据筛选）
- ✅ 交易策略（MACD、MA、KDJ策略）
- ✅ 策略回测（单策略、多策略对比）
- ✅ 选股功能（综合选股）
- ✅ 交易功能（基础交易、自动交易代码示例）
- ✅ 完整流程示例（数据→分析→回测→交易）

**运行方式**：
```bash
python examples/complete_example.py
```

---

### 2. `example.py` - 基础使用示例
**适合快速上手的示例**，展示基本功能：

- 基本使用流程（数据下载 → 分析 → 回测）
- 数据管理功能
- 多策略对比
- 组合策略
- 批量操作
- 选股功能

**运行方式**：
```bash
python examples/example.py
```

---

### 3. `trade_example.py` - 交易功能示例
**专门展示交易相关功能**：

- 基本交易操作（查询账户、持仓、买入、卖出、撤单）
- 自动交易（根据策略信号自动执行）
- 使用完整框架进行交易
- 持仓管理

**注意事项**：
- ⚠️ 涉及实盘交易，请谨慎操作
- 需要连接 MiniQMT 客户端
- 建议先在模拟环境测试

**运行方式**：
```bash
python examples/trade_example.py
```

---

### 4. `async_trade_monitor_example.py` - 异步交易+实时监控示例
**展示异步交易和实时监控功能**：

- 异步交易+自动监控
- 注册自定义回调函数
- 批量异步交易

**运行方式**：
```bash
python examples/async_trade_monitor_example.py
```

---

### 5. `stock_selection_example.py` - 选股功能示例
**专门展示选股功能**：

- 基础选股
- 价值投资选股（低PE、低PB、高ROE）
- 成长投资选股（高增长、高ROE）
- 自定义股票列表选股
- 详细分析单只股票

**运行方式**：
```bash
python examples/stock_selection_example.py
```

---

---

## 🚀 快速开始

### 方式1：运行完整功能示例（推荐）

```bash
# 运行所有功能示例
python examples/complete_example.py
```

### 方式2：运行基础示例

```bash
# 运行基础使用示例
python examples/example.py
```

### 方式3：运行特定功能示例

```bash
# 选股功能
python examples/stock_selection_example.py

# 交易功能（需要连接MiniQMT）
python examples/trade_example.py
```

---

## 📊 文件结构说明

```
examples/
├── main.py                          # QuantFramework 类定义（核心类）
├── complete_example.py              # 完整功能示例（推荐）
│
├── data_example.py                  # 数据管理功能示例
├── analysis_example.py              # 分析功能示例
├── strategy_example.py              # 策略功能示例
├── backtest_example.py              # 回测功能示例
├── stock_selection_example.py       # 选股功能示例
├── trade_example.py                 # 交易功能示例
├── async_trade_monitor_example.py   # 异步交易监控示例
│
├── example.py                       # 基础使用示例（旧版，保留兼容）
└── README.md                        # 本说明文件
```

---

## 📝 示例使用说明

### 配置参数

大部分示例文件中的配置参数（如 `qmt_path`、`account_id`）需要根据实际情况修改：

```python
# 示例中的配置
qmt_path = r'E:\国金QMT交易端模拟\userdata_mini'
account_id = '8880835625'

# 请修改为你的实际路径和账户ID
```

### 运行特定示例函数

每个示例文件都包含多个示例函数，可以在文件末尾取消注释来运行：

```python
if __name__ == "__main__":
    example_1_basic_usage()  # 运行示例1
    # example_2_data_management()  # 取消注释以运行示例2
```

### 注意事项

1. **数据依赖**：部分示例需要先下载数据，请确保 MiniQMT 已启动
2. **交易功能**：涉及交易的示例需要连接 MiniQMT 并登录交易账户
3. **图表显示**：图表绘制相关的示例可能需要图形界面支持
4. **测试环境**：建议先在测试环境或模拟账户中验证策略

---

## 📚 示例分类

### 数据相关
- `data_example.py` → 所有数据管理示例
- `complete_example.py` → `example_data_market()`, `example_data_financial()`

### 分析相关
- `analysis_example.py` → 所有分析功能示例
- `complete_example.py` → `example_technical_analysis()`, `example_fundamental_analysis()`

### 策略相关
- `strategy_example.py` → 所有策略功能示例
- `complete_example.py` → `example_strategies()`

### 回测相关
- `backtest_example.py` → 所有回测功能示例
- `complete_example.py` → `example_backtest()`

### 选股相关
- `stock_selection_example.py` → 所有选股功能示例
- `complete_example.py` → `example_stock_selection()`

### 交易相关
- `trade_example.py` → 所有交易功能示例
- `async_trade_monitor_example.py` → 异步交易监控示例
- `complete_example.py` → `example_trading_basic()`, `example_trading_auto()`

### 完整流程
- `complete_example.py` → `example_complete_workflow()`, `example_complete_with_trading()`

---

## 💡 使用建议

1. **初学者**：从 `example.py` 开始，了解基本功能
2. **全面了解**：运行 `complete_example.py` 查看所有功能
3. **特定功能**：查看对应的专门示例文件（如 `stock_selection_example.py`）
4. **实际应用**：参考 `main.py` 了解如何在实际项目中使用框架

---

## ⚠️ 重要提示

- 交易相关示例涉及实际资金操作，请谨慎使用
- 建议先在模拟环境或小资金测试所有策略
- 确保 MiniQMT 客户端已正确配置并登录
- 数据下载可能需要一定时间，请耐心等待
