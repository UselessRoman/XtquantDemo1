# utils.py
"""
工具函数模块
提供一些通用的辅助函数
作者：WJC
日期：2026.1.5
"""

from datetime import datetime, timedelta
from typing import Optional
import pandas as pd


def format_date(date_input) -> str:
    """
    格式化日期为YYYYMMDD格式
    
    Args:
        date_input: 可以是字符串(YYYYMMDD或YYYY-MM-DD)、datetime对象或None
        
    Returns:
        str: YYYYMMDD格式的日期字符串
    """
    if date_input is None:
        return None
    
    if isinstance(date_input, str):
        # 如果是YYYY-MM-DD格式，转换为YYYYMMDD
        if '-' in date_input:
            try:
                dt = datetime.strptime(date_input, '%Y-%m-%d')
                return dt.strftime('%Y%m%d')
            except:
                pass
        # 如果已经是YYYYMMDD格式，直接返回
        elif len(date_input) == 8:
            return date_input
    
    if isinstance(date_input, datetime):
        return date_input.strftime('%Y%m%d')
    
    return str(date_input)


def get_trading_days_count(start_date: str, end_date: str) -> int:
    """
    估算交易日数量（简单估算，不考虑节假日）
    
    Args:
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
        
    Returns:
        int: 估算的交易日数量
    """
    try:
        start = datetime.strptime(start_date, '%Y%m%d')
        end = datetime.strptime(end_date, '%Y%m%d')
        days = (end - start).days
        # 简单估算：约70%的日期是交易日
        trading_days = int(days * 0.7)
        return max(trading_days, 0)
    except:
        return 0


def validate_stock_code(stock_code: str) -> bool:
    """
    验证股票代码格式
    
    Args:
        stock_code: 股票代码，如 '002352.SZ' 或 '600519.SH'
        
    Returns:
        bool: 是否有效
    """
    if not stock_code or '.' not in stock_code:
        return False
    
    parts = stock_code.split('.')
    if len(parts) != 2:
        return False
    
    code, market = parts
    if market not in ['SZ', 'SH']:
        return False
    
    if not code.isdigit() or len(code) != 6:
        return False
    
    return True


def get_next_trading_date(date_str: str) -> str:
    """
    获取下一个交易日（简单实现，不考虑节假日）
    
    Args:
        date_str: 日期字符串 YYYYMMDD
        
    Returns:
        str: 下一个交易日 YYYYMMDD
    """
    try:
        dt = datetime.strptime(date_str, '%Y%m%d')
        # 简单加1天，实际应该考虑交易日历
        next_date = dt + timedelta(days=1)
        return next_date.strftime('%Y%m%d')
    except:
        return date_str


def format_number(num: float, decimals: int = 2) -> str:
    """
    格式化数字显示
    
    Args:
        num: 数字
        decimals: 小数位数
        
    Returns:
        str: 格式化后的字符串
    """
    if pd.isna(num):
        return 'N/A'
    
    # 确保至少显示两位小数（即使decimals=0）
    actual_decimals = max(decimals, 2) if decimals == 0 else decimals
    
    if abs(num) >= 1e8:
        return f"{num / 1e8:.{actual_decimals}f}亿"
    elif abs(num) >= 1e4:
        return f"{num / 1e4:.{actual_decimals}f}万"
    else:
        return f"{num:.{actual_decimals}f}"
