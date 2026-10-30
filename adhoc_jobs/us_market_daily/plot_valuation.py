"""Plot computed valuation scenarios. No generated or interpolated market prices."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--out', required=True, type=Path)
args = parser.parse_args()
data = json.loads((args.out / 'google_valuation_model.json').read_text())
font = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
font_manager.fontManager.addfont(font)
plt.rcParams.update({'font.family': font_manager.FontProperties(fname=font).get_name(),
                     'font.size': 11, 'axes.unicode_minus': False})
fig, axes = plt.subplots(2, 1, figsize=(12, 9), gridspec_kw={'height_ratios': [1, 1.1]})
fig.set_facecolor('#f5f7fa')
colors = ['#b45b40', '#19756b', '#526ab5']
for scenario, color in zip(data['scenarios'], colors):
    rows = scenario['forecast']
    axes[0].plot([r['year'] for r in rows], [r['fcff_B'] for r in rows],
                 marker='o', lw=2, color=color, label=f"{scenario['name']} · 现值 ${scenario['price_usd']:.0f}")
axes[0].axhline(0, color='#88939e', lw=.8)
axes[0].set_title('未来经济自由现金流：模型预测，不是历史行情', loc='left', pad=15)
axes[0].set_ylabel('十亿美元 / 年')
axes[0].set_xlabel('未来第几年（基线截至2026年6月；估值日2026-10-28）')
axes[0].set_xticks(range(1, 11))
axes[0].legend(frameon=False, ncol=3, loc='upper left')
axes[0].grid(axis='y', alpha=.2)
rates = sorted({r['wacc'] for r in data['sensitivity']})
growths = sorted({r['terminal_growth'] for r in data['sensitivity']})
values = np.array([[next(x['price_usd'] for x in data['sensitivity'] if x['wacc'] == r and x['terminal_growth'] == g)
                    for g in growths] for r in rates])
axes[1].imshow(values, cmap='YlGnBu', aspect='auto')
axes[1].set_xticks(range(len(growths)), [f'{g*100:g}%' for g in growths])
axes[1].set_yticks(range(len(rates)), [f'{r*100:g}%' for r in rates])
axes[1].set_xlabel('永续增长率（改变增长衰减终点，其余基准参数固定）')
axes[1].set_ylabel('折现率 WACC')
for y, row in enumerate(values):
    for x, number in enumerate(row):
        axes[1].text(x, y, f'${number:.0f}', ha='center', va='center', fontsize=13,
                     color='white' if number > np.percentile(values, 60) else '#142a36')
axes[1].set_title('基准经营情景的估值敏感性 · 每股美元；对比收盘 $320.58', loc='left', pad=15)
for ax in axes:
    ax.spines[['top', 'right']].set_visible(False)
fig.suptitle('Google：现金投入与长期回报如何改变估值', x=.08, ha='left', fontsize=19, fontweight='bold')
fig.text(.08, .018, '来源：本次自建模型及公开财报；SBC保留为成本，融资资本开支已计入。所有未来曲线、参数与估值均为研究假设。', fontsize=10, color='#586878')
fig.subplots_adjust(left=.10, right=.96, bottom=.10, top=.90, hspace=.5)
fig.savefig(args.out / 'google_valuation_scenarios.png', dpi=160, facecolor=fig.get_facecolor())
plt.close(fig)
print(args.out / 'google_valuation_scenarios.png')
