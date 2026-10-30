"""Collect a dated public-market sample, preserving raw responses and chart inputs."""
import json
from pathlib import Path
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from zoneinfo import ZoneInfo
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'contexts/survey_sessions/a_share_daily/2026-10-28'
OUT.mkdir(parents=True, exist_ok=True)
ASOF = '2026-10-27'
SYMBOLS = {'sh000001':'上证指数','sh000016':'上证50','sh000300':'沪深300','sh000688':'科创50','sh510050':'上证50ETF · 510050','sh510300':'沪深300ETF · 510300','sh588000':'科创50ETF · 588000'}

def fetch(symbol):
    url = f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={symbol},day,,,80,qfq'
    raw = subprocess.check_output(['curl','--fail','--silent','--show-error','--max-time','25',url],text=True)
    (OUT / f'{symbol}_raw.json').write_text(raw)
    data = json.loads(raw)['data'][symbol]
    # The response itself determines whether adjusted data is available.
    key = 'qfqday' if 'qfqday' in data else 'day'
    rows = [r for r in data[key] if r[0] <= ASOF]
    assert len(rows) >= 21 and rows[-1][0] == ASOF, (symbol, rows[-1][0])
    assert len({r[0] for r in rows}) == len(rows)
    closes = [float(r[2]) for r in rows]
    return symbol, {'name':SYMBOLS[symbol], 'source':url, 'price_basis':key,
        'session':ASOF, 'close':closes[-1], 'daily_pct':(closes[-1]/closes[-2]-1)*100,
        'twenty_session_pct':(closes[-1]/closes[-21]-1)*100,
        'rows':rows[-21:]}

with ThreadPoolExecutor(max_workers=4) as pool:
    metrics = dict(pool.map(fetch, SYMBOLS))
(OUT/'market.json').write_text(json.dumps({'collected_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'asof':ASOF,'provider':'腾讯财经公开行情；第三方数据','metrics':metrics},ensure_ascii=False,indent=2))
font_manager.fontManager.addfont('/System/Library/Fonts/Supplemental/Arial Unicode.ttf')
plt.rcParams.update({'font.family':'Arial Unicode MS','axes.unicode_minus':False,'font.size':11})
fig = plt.figure(figsize=(12,10),facecolor='#f6f8fc')
fig.text(.08,.95,'A 股晨报｜ETF · 上证 · 科创',fontsize=24,weight='bold',color='#20304a')
fig.text(.08,.915,'2026-10-28 样稿  /  数据截至 10 月 27 日收盘  /  不含今日盘中',color='#65748b')
colors = ['#247c91','#6674d6','#cc9136','#b15280']
ax=fig.add_axes([.09,.54,.83,.29])
for symbol,color in zip(list(SYMBOLS)[:4],colors):
    m=metrics[symbol];rows=m['rows'];base=float(rows[0][2])
    ax.plot(range(21),[float(r[2])/base*100 for r in rows],label=m['name'],color=color,lw=2)
    assert [r[0] for r in rows] == [r[0] for r in metrics['sh000001']['rows']]
ax.set_title('近 20 个交易日区间表现｜起点 = 100，指数价格回报',loc='left',pad=16)
ax.set_xticks([0,5,10,15,20],[metrics['sh000001']['rows'][i][0][5:] for i in [0,5,10,15,20]])
ax.legend(ncol=4,loc='upper center',bbox_to_anchor=(.5,1.02),frameon=False)
ax.grid(axis='y',alpha=.18);ax.spines[['top','right']].set_visible(False)
bx=fig.add_axes([.25,.16,.64,.25])
keys=['sh000001','sh000016','sh000300','sh000688','sh510050','sh510300','sh588000']
values=[metrics[k]['daily_pct'] for k in keys]
bx.barh([metrics[k]['name'] for k in keys],values,color=['#b45464' if v<0 else '#288b83' for v in values])
bx.invert_yaxis();bx.axvline(0,color='#999',lw=.8);bx.set_xlim(min(values)-1,max(0,max(values))+1)
for i,v in enumerate(values):bx.text(v-.10 if v<0 else v+.10,i,f'{v:+.2f}%',va='center',ha='right' if v<0 else 'left',fontsize=10)
bx.set_title('上一交易日涨跌幅｜指数与 ETF 分开展示',loc='left',pad=15)
bx.set_xlabel('日涨跌幅（%）');bx.spines[['top','right','left']].set_visible(False)
fig.text(.08,.055,'来源：腾讯财经公开日线；ETF 使用接口前复权序列，指数使用价格指数。',fontsize=10,color='#65748b')
fig.text(.08,.03,'图表用于市场观察。成交额、基金份额、净申购和估值分位需分别核验，不能从涨跌幅推断。',fontsize=10,color='#65748b')
fig.savefig(OUT/'market.png',dpi=170,facecolor=fig.get_facecolor())
fig.savefig(OUT/'market.svg',facecolor=fig.get_facecolor())
print(json.dumps({k:{x:v for x,v in m.items() if x!='rows'} for k,m in metrics.items()},ensure_ascii=False,indent=2))
