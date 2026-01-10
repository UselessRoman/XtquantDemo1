# run_tests.py
"""
运行测试脚本
提供便捷的测试运行方式
"""

import sys
import subprocess
import argparse
import shutil


def run_tests(test_type='all', verbose=True, coverage=True):
    """
    运行测试
    
    Args:
        test_type: 测试类型 ('all', 'unit', 'integration', 'quick')
        verbose: 是否显示详细信息
        coverage: 是否生成覆盖率报告
    """
    # 检查 pytest 是否可用
    pytest_cmd = shutil.which('pytest')
    
    if not pytest_cmd:
        # 尝试使用 python -m pytest
        cmd = [sys.executable, '-m', 'pytest']
    else:
        cmd = ['pytest']
    
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=src', '--cov-config=.coveragerc', '--cov-report=html', '--cov-report=term'])
    
    # 根据测试类型选择测试文件
    if test_type == 'unit':
        cmd.extend([
            'tests/test_config.py',
            'tests/test_utils.py',
            'tests/test_market_data.py',
            'tests/test_financial_data.py',
            'tests/test_technical.py',
            'tests/test_fundamental.py',
            'tests/test_strategies.py',
            'tests/test_backtest.py',
            'tests/test_selector.py'
        ])
    elif test_type == 'integration':
        cmd.append('tests/test_integration.py')
    elif test_type == 'quick':
        cmd.extend([
            'tests/test_config.py',
            'tests/test_utils.py'
        ])
    elif test_type == 'all':
        cmd.append('tests/')
    else:
        print(f"未知的测试类型: {test_type}")
        print("可用类型: all, unit, integration, quick")
        return False
    
    print(f"\n运行测试: {test_type}")
    print(f"命令: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except FileNotFoundError as e:
        print(f"错误: 找不到 pytest 命令")
        print(f"请确保已安装 pytest: pip install pytest pytest-cov")
        return False
    except Exception as e:
        print(f"运行测试时出错: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='运行测试')
    parser.add_argument(
        '--type', '-t',
        choices=['all', 'unit', 'integration', 'quick'],
        default='all',
        help='测试类型'
    )
    parser.add_argument(
        '--no-coverage', '-nc',
        action='store_true',
        help='不生成覆盖率报告'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='安静模式（不显示详细信息）'
    )
    
    args = parser.parse_args()
    
    success = run_tests(
        test_type=args.type,
        verbose=not args.quiet,
        coverage=not args.no_coverage
    )
    
    if success:
        print("\n[成功] 所有测试通过")
        if not args.no_coverage:
            print("覆盖率报告已生成: htmlcov/index.html")
    else:
        print("\n[失败] 部分测试失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
