# data_example.py
"""
数据管理功能示例
展示如何使用行情数据和财务数据管理功能
"""

import sys
import os

# 添加项目根目录到路径
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from examples.main import QuantFramework
from src.data.market_data import MarketDataManager
from src.data.financial_data import FinancialDataManager


def example_market_data():
    """示例1：行情数据管理"""
    print("\n" + "=" * 60)
    print("示例1：行情数据管理")
    print("=" * 60)
    
    # 方式1：使用框架
    framework = QuantFramework()
    stock_code = '002352.SZ'
    
    print("\n【使用框架】")
    print("-" * 60)
    
    # 下载历史数据
    print("\n1. 下载历史数据")
    success = framework.download_data(stock_code, '1d', '20240101', '20241231')
    print(f"下载结果: {'成功' if success else '失败'}")
    
    # 获取本地数据
    print("\n2. 获取本地数据")
    data = framework.get_data(stock_code, '1d', '20240101', '20241231')
    if data is not None:
        print(f"数据条数: {len(data)}")
        print(f"日期范围: {data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}")
        print(f"最新收盘价: {data['close'].iloc[-1]:.2f}")
    
    # 增量更新数据
    print("\n3. 增量更新数据")
    update_success = framework.update_data(stock_code, '1d')
    print(f"更新结果: {'成功' if update_success else '失败'}")
    
    # 方式2：直接使用管理器
    print("\n【直接使用管理器】")
    print("-" * 60)
    manager = MarketDataManager()
    
    # 批量下载
    print("\n4. 批量下载数据")
    stock_list = ['002352.SZ', '600519.SH', '000001.SZ']
    results = manager.batch_download(stock_list, '1d', '20240101', '20241231')
    for code, success in results.items():
        print(f"  {code}: {'成功' if success else '失败'}")
    
    # 获取数据信息
    print("\n5. 获取数据信息")
    info = manager.get_data_info(stock_code, '1d')
    if info:
        for key, value in info.items():
            print(f"  {key}: {value}")


def example_financial_data():
    """示例2：财务数据管理"""
    print("\n" + "=" * 60)
    print("示例2：财务数据管理")
    print("=" * 60)
    
    manager = FinancialDataManager()
    stock_code = '600519.SH'
    
    # 获取财务数据
    print(f"\n1. 获取 {stock_code} 的财务数据")
    print("-" * 60)
    financial_data = manager.get_financial_data(stock_code, auto_download=True)
    if financial_data:
        print("财务指标:")
        for key, value in financial_data.items():
            if isinstance(value, (int, float)):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
    else:
        print("未能获取财务数据")
    
    # 批量获取财务数据
    print("\n2. 批量获取财务数据")
    print("-" * 60)
    stock_list = ['600519.SH', '000001.SZ', '002352.SZ']
    all_data = manager.batch_get_financial_data(stock_list, auto_download=False)
    for code, data in all_data.items():
        if data:
            pe = data.get('pe', 'N/A')
            roe = data.get('roe', 'N/A')
            pb = data.get('pb', 'N/A')
            print(f"  {code}: PE={pe}, ROE={roe}%, PB={pb}")
    
    # 下载财务数据
    print("\n3. 下载财务数据到本地")
    print("-" * 60)
    table_list = ['Balance', 'Income', 'CashFlow']
    download_success = manager.download_financial_data(
        stock_list, table_list=table_list
    )
    print(f"下载结果: {'成功' if download_success else '失败'}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("数据管理功能示例")
    print("=" * 60)
    
    # 运行示例（根据需要取消注释）
    example_market_data()
    # example_financial_data()
    
    print("\n提示：取消注释上面的示例函数以运行相应示例")
