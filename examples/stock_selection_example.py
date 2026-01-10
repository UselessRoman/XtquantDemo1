# stock_selection_example.py
"""
选股功能使用示例
展示如何使用选股模块进行A股选股
作者：WJC
日期：2026.1.5
"""

from src.selection.selector import StockSelector
import pandas as pd


def example_1_basic_selection():
    """示例1：基础选股"""
    print("\n" + "=" * 60)
    print("示例1：基础选股")
    print("=" * 60)
    
    selector = StockSelector()
    
    # 基础选股条件
    financial_filters = {
        'min_pe': 0,
        'max_pe': 30,  # PE小于30
        'min_pb': 0,
        'max_pb': 5,   # PB小于5
        'min_roe': 10,  # ROE大于10%
        'min_profit_growth': 10  # 净利润增长率大于10%
    }
    
    technical_filters = {
        'min_technical_score': 40,
        'require_above_ma20': True  # 要求价格在MA20之上
    }
    
    # 执行选股
    result = selector.select_stocks(
        financial_filters=financial_filters,
        technical_filters=technical_filters,
        min_total_score=60.0,
        max_results=20
    )
    
    if not result.empty:
        print("\n选股结果:")
        print("=" * 60)
        print(result.to_string(index=False))
        
        # 保存结果
        selector.save_selection_result(result)
    else:
        print("\n未选出符合条件的股票")


def example_2_value_investment():
    """示例2：价值投资选股（低PE、低PB、高ROE）"""
    print("\n" + "=" * 60)
    print("示例2：价值投资选股")
    print("=" * 60)
    
    selector = StockSelector()
    
    # 价值投资筛选条件
    financial_filters = {
        'min_pe': 0,
        'max_pe': 15,  # PE小于15
        'min_pb': 0,
        'max_pb': 3,   # PB小于3
        'min_roe': 15,  # ROE大于15%
        'min_profit_growth': 5
    }
    
    technical_filters = {
        'min_technical_score': 30,  # 技术得分要求较低
        'require_above_ma20': False
    }
    
    result = selector.select_stocks(
        financial_filters=financial_filters,
        technical_filters=technical_filters,
        min_total_score=55.0,  # 更注重财务指标
        max_results=30
    )
    
    if not result.empty:
        print("\n价值投资选股结果:")
        print("=" * 60)
        # 显示前10名
        print(result.head(10).to_string(index=False))
        selector.save_selection_result(result, 'value_investment_selection.csv')


def example_3_growth_investment():
    """示例3：成长投资选股（高增长、高ROE）"""
    print("\n" + "=" * 60)
    print("示例3：成长投资选股")
    print("=" * 60)
    
    selector = StockSelector()
    
    # 成长投资筛选条件
    financial_filters = {
        'min_pe': 0,
        'max_pe': 50,  # PE可以较高
        'min_pb': 0,
        'max_pb': 10,
        'min_roe': 20,  # 高ROE
        'min_profit_growth': 30  # 高增长
    }
    
    technical_filters = {
        'min_technical_score': 50,  # 技术得分要求较高
        'require_above_ma20': True
    }
    
    result = selector.select_stocks(
        financial_filters=financial_filters,
        technical_filters=technical_filters,
        min_total_score=65.0,
        max_results=20
    )
    
    if not result.empty:
        print("\n成长投资选股结果:")
        print("=" * 60)
        print(result.to_string(index=False))
        selector.save_selection_result(result, 'growth_investment_selection.csv')


def example_4_custom_stock_list():
    """示例4：自定义股票列表选股"""
    print("\n" + "=" * 60)
    print("示例4：自定义股票列表选股")
    print("=" * 60)
    
    selector = StockSelector()
    
    # 自定义股票列表（例如：特定行业或自选股）
    custom_stocks = [
        '000001.SZ',  # 平安银行
        '600519.SH',  # 贵州茅台
        '000858.SZ',  # 五粮液
        '002352.SZ',  # 顺丰控股
        '600036.SH',  # 招商银行
        '000063.SZ',  # 中兴通讯
    ]
    
    financial_filters = {
        'min_pe': 0,
        'max_pe': 40,
        'min_pb': 0,
        'max_pb': 8,
        'min_roe': 8,
        'min_profit_growth': 0
    }
    
    technical_filters = {
        'min_technical_score': 35,
        'require_above_ma20': False
    }
    
    result = selector.select_stocks(
        stock_list=custom_stocks,
        financial_filters=financial_filters,
        technical_filters=technical_filters,
        min_total_score=50.0,
        max_results=10
    )
    
    if not result.empty:
        print("\n自定义股票列表选股结果:")
        print("=" * 60)
        print(result.to_string(index=False))


def example_5_detailed_analysis():
    """示例5：详细分析单只股票"""
    print("\n" + "=" * 60)
    print("示例5：详细分析单只股票")
    print("=" * 60)
    
    selector = StockSelector()
    stock_code = '002352.SZ'
    
    # 获取财务数据
    print(f"\n分析股票: {stock_code}")
    print("-" * 60)
    
    financial_data = selector.get_financial_data(stock_code)
    if financial_data:
        print("\n财务数据:")
        for key, value in financial_data.items():
            print(f"  {key}: {value}")
        
        financial_score = selector.get_financial_score(financial_data)
        if financial_score:
            print(f"\n财务得分: {financial_score['score']}/{financial_score['max_score']}")
            print("得分详情:")
            for key, value in financial_score['details'].items():
                print(f"  {key}: {value}")
    
    # 获取技术得分
    print("\n" + "-" * 60)
    technical_score = selector.get_technical_score(stock_code)
    if technical_score:
        print("\n技术得分:")
        print(f"  得分: {technical_score['score']}/{technical_score['max_score']}")
        print(f"  最新价格: {technical_score['latest_price']:.2f}")
        if technical_score.get('ma5'):
            print(f"  MA5: {technical_score['ma5']:.2f}")
        if technical_score.get('ma10'):
            print(f"  MA10: {technical_score['ma10']:.2f}")
        if technical_score.get('ma20'):
            print(f"  MA20: {technical_score['ma20']:.2f}")
        print("得分详情:")
        for key, value in technical_score['details'].items():
            print(f"  {key}: {value}")
        
        # 计算总分
        if financial_score:
            total_score = financial_score['score'] * 0.6 + technical_score['score'] * 0.4
            print(f"\n总分: {total_score:.2f} (财务60% + 技术40%)")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("A股选股功能示例")
    print("=" * 60)
    print("\n注意：选股需要连接MiniQMT并下载数据")
    print("建议先下载目标股票的历史数据")
    print("\n" + "=" * 60)
    
    # 运行示例（根据需要取消注释）
    
    # example_1_basic_selection()
    # example_2_value_investment()
    # example_3_growth_investment()
    # example_4_custom_stock_list()
    # example_5_detailed_analysis()
    
    print("\n提示：取消注释上面的示例函数以运行相应示例")
