# analysis_example.py
"""
分析功能示例
展示如何使用技术分析和财务分析功能
"""

import sys
import os

# 添加项目根目录到路径
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from examples.main import QuantFramework
from src.analysis.technical import TechnicalIndicators, ChartPlotter
from src.analysis.fundamental import FundamentalAnalyzer
from src.data.market_data import MarketDataManager
from src.data.financial_data import FinancialDataManager
import matplotlib.pyplot as plt


def example_technical_analysis():
    """示例1：技术指标分析"""
    print("\n" + "=" * 60)
    print("示例1：技术指标分析")
    print("=" * 60)
    
    # 方式1：使用框架
    framework = QuantFramework()
    stock_code = '002352.SZ'
    
    print("\n【使用框架进行分析】")
    print("-" * 60)
    framework.analyze_data(stock_code, '1d', '20240101', '20241231', save_chart=False)
    
    # 方式2：直接使用分析工具
    print("\n【直接使用分析工具】")
    print("-" * 60)
    manager = MarketDataManager()
    calculator = TechnicalIndicators()
    
    # 获取数据
    data = manager.get_local_data(stock_code, '1d', '20240101', '20241231')
    if data is None or data.empty:
        print("[错误] 无法获取数据，请先下载数据")
        return
    
    # 计算所有技术指标
    print("\n1. 计算技术指标")
    indicators = calculator.calculate_all(data)
    print("已计算指标: MA、MACD、KDJ、RSI")
    
    # 显示最新指标值
    if 'ma' in indicators and not indicators['ma'].empty:
        latest_ma = indicators['ma'].iloc[-1]
        print("\n最新均线值:")
        for col in ['MA5', 'MA10', 'MA20']:
            if col in latest_ma and not latest_ma[col] is not None:
                print(f"  {col}: {latest_ma[col]:.2f}")
    
    # 绘制图表
    print("\n2. 绘制技术分析图表")
    plotter = ChartPlotter()
    try:
        fig, axes = plotter.create_chart(data, indicators, stock_code)
        print("[成功] 图表已生成")
        plt.close(fig)  # 关闭图表，避免阻塞
    except Exception as e:
        print(f"[提示] 图表生成跳过: {e}")


def example_fundamental_analysis():
    """示例2：财务指标分析"""
    print("\n" + "=" * 60)
    print("示例2：财务指标分析")
    print("=" * 60)
    
    manager = FinancialDataManager()
    analyzer = FundamentalAnalyzer()
    stock_code = '600519.SH'
    
    # 获取财务数据
    print(f"\n分析股票: {stock_code}")
    print("-" * 60)
    financial_data = manager.get_financial_data(stock_code, auto_download=False)
    if not financial_data:
        print("[错误] 无法获取财务数据")
        return
    
    # 计算财务得分
    print("\n1. 计算财务得分")
    score_result = analyzer.calculate_financial_score(financial_data)
    if score_result:
        print(f"财务得分: {score_result['score']}/{score_result['max_score']}")
        print("得分详情:")
        for key, value in score_result['details'].items():
            print(f"  {key}: {value}")
    
    # 财务数据筛选
    print("\n2. 财务数据筛选")
    filters = {
        'max_pe': 30,
        'min_roe': 10,
        'min_profit_growth': 5
    }
    passed = analyzer.filter_financial_data(financial_data, filters)
    print(f"筛选结果: {'通过' if passed else '未通过'}")
    print(f"筛选条件: {filters}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("分析功能示例")
    print("=" * 60)
    
    # 运行示例（根据需要取消注释）
    example_technical_analysis()
    # example_fundamental_analysis()
    
    print("\n提示：取消注释上面的示例函数以运行相应示例")
