# chart.py
"""
技术分析图表绘制模块
功能：绘制专业的技术分析图表（K线、指标等）
作者：WJC
日期：2026.1.5
"""

import numpy as np
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from typing import Dict, Tuple
import warnings
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.config import ChartConfig

warnings.filterwarnings('ignore')


class ChartPlotter:
    """专业图表绘制器"""
    
    def __init__(self, config: ChartConfig = None):
        self.config = config or ChartConfig()
        self._setup_fonts()
    
    def _setup_fonts(self):
        """设置字体"""
        plt.rcParams['font.family'] = self.config.FONT_CONFIG['family']
        plt.rcParams['axes.unicode_minus'] = False
    
    def create_chart(self, data: pd.DataFrame, indicators: Dict[str, pd.DataFrame],
                     symbol: str) -> Tuple[plt.Figure, list]:
        """
        创建专业图表
        
        Args:
            data: 股票数据
            indicators: 技术指标字典
            symbol: 股票代码
            
        Returns:
            Tuple: (figure, axes)
        """
        # 创建addplot列表
        add_plots = self._create_addplots(data, indicators)
        
        # 创建样式
        style = self._create_style()
        
        # 绘制图表
        fig, axes = mpf.plot(
            data,
            type='candle',
            style=style,
            addplot=add_plots,
            volume=False,
            panel_ratios=self.config.LAYOUT['panel_ratios'],
            figsize=self.config.LAYOUT['figsize'],
            title=f'{symbol} Technical Analysis',
            ylabel='Price',
            datetime_format='%Y-%m-%d',
            xrotation=45,
            tight_layout=True,
            returnfig=True,
            show_nontrading=False,
            scale_padding={'left': 0.1, 'right': 0.1, 'top': 0.2, 'bottom': 0.1}
        )
        
        # 精细化调整
        self._refine_chart(fig, axes, data, indicators, symbol)
        
        return fig, axes
    
    def _create_addplots(self, data: pd.DataFrame, indicators: Dict[str, pd.DataFrame]) -> list:
        """创建addplot列表"""
        add_plots = []
        
        # 1. 主图：移动平均线
        ma_data = indicators['ma']
        colors = [self.config.COLORS['ma5'],
                  self.config.COLORS['ma10'],
                  self.config.COLORS['ma20']]
        
        for col, color in zip(ma_data.columns, colors):
            add_plots.append(mpf.make_addplot(
                ma_data[col],
                color=color,
                width=1.2,
                alpha=0.8,
                panel=0
            ))
        
        # 2. 成交量面板
        volume_colors = self._get_volume_colors(data)
        add_plots.append(mpf.make_addplot(
            data['volume'],
            type='bar',
            panel=1,
            color=volume_colors,
            alpha=0.6,
            ylabel='Volume',
            width=0.8
        ))
        
        # 3. MACD面板
        macd_data = indicators['macd']
        
        add_plots.append(mpf.make_addplot(
            macd_data['DIF'],
            panel=2,
            color=self.config.COLORS['dif'],
            width=1.0,
            alpha=0.9
        ))
        
        add_plots.append(mpf.make_addplot(
            macd_data['DEA'],
            panel=2,
            color=self.config.COLORS['dea'],
            width=1.0,
            alpha=0.9
        ))
        
        macd_colors = self._get_macd_colors(macd_data['MACD'])
        add_plots.append(mpf.make_addplot(
            macd_data['MACD'],
            type='bar',
            panel=2,
            color=macd_colors,
            alpha=0.5,
            width=0.6
        ))
        
        # 4. KDJ面板
        kdj_data = indicators['kdj']
        kdj_colors = [self.config.COLORS['k'],
                      self.config.COLORS['d'],
                      self.config.COLORS['j']]
        
        for col, color in zip(['K', 'D', 'J'], kdj_colors):
            add_plots.append(mpf.make_addplot(
                kdj_data[col],
                panel=3,
                color=color,
                width=0.8,
                alpha=0.9
            ))
        
        return add_plots
    
    def _create_style(self):
        """创建专业样式"""
        market_colors = mpf.make_marketcolors(
            up=self.config.COLORS['up'],
            down=self.config.COLORS['down'],
            edge={'up': self.config.COLORS['up'], 'down': self.config.COLORS['down']},
            wick={'up': self.config.COLORS['up'], 'down': self.config.COLORS['down']},
            volume={'up': '#FADBD8', 'down': '#D5F4E6'},
            alpha=0.9,
            inherit=True
        )
        
        style = mpf.make_mpf_style(
            base_mpf_style='classic',
            marketcolors=market_colors,
            gridstyle=':',
            gridcolor=self.config.COLORS['grid'],
            gridaxis='both',
            facecolor=self.config.COLORS['background'],
            edgecolor='#34495E',
            figcolor=self.config.COLORS['background'],
            y_on_right=False,
            rc={
                'axes.linewidth': 0.8,
                'axes.labelsize': self.config.FONT_CONFIG['size_axis'],
                'axes.titlesize': self.config.FONT_CONFIG['size_title'],
                'xtick.labelsize': self.config.FONT_CONFIG['size_tick'],
                'ytick.labelsize': self.config.FONT_CONFIG['size_tick'],
                'legend.fontsize': self.config.FONT_CONFIG['size_legend'],
                'font.family': self.config.FONT_CONFIG['family'],
                'axes.titleweight': 'bold',
                'axes.labelweight': 'bold',
            }
        )
        
        return style
    
    def _get_volume_colors(self, data: pd.DataFrame) -> list:
        """获取成交量颜色列表"""
        colors = []
        for i in range(len(data)):
            if data['close'].iloc[i] >= data['open'].iloc[i]:
                colors.append('#FADBD8')  # 浅红
            else:
                colors.append('#D5F4E6')  # 浅绿
        return colors
    
    def _get_macd_colors(self, macd_series: pd.Series) -> list:
        """获取MACD柱状图颜色列表"""
        colors = []
        for val in macd_series:
            if val >= 0:
                colors.append(self.config.COLORS['macd_positive'])
            else:
                colors.append(self.config.COLORS['macd_negative'])
        return colors
    
    def _refine_chart(self, fig: plt.Figure, axes: list, data: pd.DataFrame,
                      indicators: Dict[str, pd.DataFrame], symbol: str):
        """精细化调整图表"""
        # 清除所有自动生成的图例
        for ax in axes:
            if ax.get_legend() is not None:
                ax.get_legend().remove()
        
        # 设置主图y轴格式
        axes[0].yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.2f}'))
        
        # 设置成交量y轴格式
        axes[1].yaxis.set_major_formatter(ticker.FuncFormatter(
            lambda x, p: f'{x / 1e6:.1f}M' if x >= 1e6 else f'{x / 1e3:.0f}K'
        ))
        
        # 添加网格线
        for ax in axes:
            ax.grid(True, linestyle=':', alpha=0.3, color=self.config.COLORS['grid'])
        
        # MACD面板：添加零轴线
        axes[2].axhline(y=0, color='#34495E', linestyle='-', linewidth=0.8, alpha=0.5)
        
        # MACD填充区域
        macd_data = indicators['macd']
        axes[2].fill_between(data.index, 0, macd_data['MACD'].values,
                             where=macd_data['MACD'] >= 0,
                             color=self.config.COLORS['macd_positive'], alpha=0.1)
        axes[2].fill_between(data.index, 0, macd_data['MACD'].values,
                             where=macd_data['MACD'] < 0,
                             color=self.config.COLORS['macd_negative'], alpha=0.1)
        
        # KDJ面板：添加参考线
        axes[3].axhline(y=80, color='#E74C3C', linestyle='--', linewidth=1.0, alpha=0.7)
        axes[3].axhline(y=20, color='#2ECC71', linestyle='--', linewidth=1.0, alpha=0.7)
        axes[3].axhline(y=50, color='#95A5A6', linestyle=':', linewidth=0.8, alpha=0.5)
        
        # KDJ填充区域
        axes[3].fill_between(data.index, 80, 100, color='#FADBD8', alpha=0.1)
        axes[3].fill_between(data.index, 0, 20, color='#D5F4E6', alpha=0.1)
        
        # 手动添加图例
        # 主图图例
        legend_elements0 = [
            Line2D([0], [0], color='black', lw=2, label='Candlestick'),
            Line2D([0], [0], color=self.config.COLORS['ma5'], lw=1.2, label='MA5'),
            Line2D([0], [0], color=self.config.COLORS['ma10'], lw=1.2, label='MA10'),
            Line2D([0], [0], color=self.config.COLORS['ma20'], lw=1.2, label='MA20')
        ]
        axes[0].legend(handles=legend_elements0, loc='upper left',
                       frameon=True, framealpha=0.9, edgecolor='gray')
        
        # MACD图例
        legend_elements2 = [
            Line2D([0], [0], color=self.config.COLORS['dif'], lw=1.0, label='DIF'),
            Line2D([0], [0], color=self.config.COLORS['dea'], lw=1.0, label='DEA'),
            mpatches.Patch(color='gray', alpha=0.5, label='MACD Bar')
        ]
        axes[2].legend(handles=legend_elements2, loc='upper left',
                       frameon=True, framealpha=0.9, edgecolor='gray')
        
        # KDJ图例
        legend_elements3 = [
            Line2D([0], [0], color=self.config.COLORS['k'], lw=0.8, label='K'),
            Line2D([0], [0], color=self.config.COLORS['d'], lw=0.8, label='D'),
            Line2D([0], [0], color=self.config.COLORS['j'], lw=0.8, label='J')
        ]
        axes[3].legend(handles=legend_elements3, loc='upper left',
                       frameon=True, framealpha=0.9, edgecolor='gray')
        
        # 设置坐标轴标签
        labels = ['Price', 'Volume', 'MACD', 'KDJ']
        for ax, label in zip(axes, labels):
            ax.set_ylabel(label, fontsize=11, fontweight='bold', labelpad=10)
        
        # 添加边框
        for ax in axes:
            for spine in ax.spines.values():
                spine.set_linewidth(0.8)
                spine.set_color('#BDC3C7')
        
        # 调整布局
        plt.subplots_adjust(
            left=self.config.LAYOUT['margin_left'],
            right=self.config.LAYOUT['margin_right'],
            bottom=self.config.LAYOUT['margin_bottom'],
            top=self.config.LAYOUT['margin_top'],
            hspace=self.config.LAYOUT['hspace']
        )
        
        # 添加数据范围说明
        date_range = f"{data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}"
        fig.text(0.01, 0.01, date_range,
                 fontsize=9, color='#7F8C8D', alpha=0.7)
