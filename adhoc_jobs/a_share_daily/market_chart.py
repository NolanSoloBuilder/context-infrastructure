"""Render verified snapshots without fetching or changing their data."""
from html import escape
import math

def render_market_svg(metrics, asof, fallback=False):
    if not metrics or any(not math.isfinite(m['daily_pct']) for m in metrics.values()):
        raise ValueError('Daily changes must be finite')
    w,h=1100,730
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="#fff"/><g font-family="Arial, PingFang SC, sans-serif" fill="#24323d">',f'<text x="40" y="38" font-size="23">指数与ETF · {asof} 收盘</text>', '<text x="40" y="70" font-size="15">近20交易日指数价格表现 · 起点100</text>']
    keys=list(metrics)[:4];colors=['#247c91','#6674d6','#cc9136','#b15280']
    series=[[float(r[2])/float(metrics[k]['rows'][0][2])*100 for r in metrics[k]['rows']] for k in keys]
    lo=min(min(a) for a in series)-2;hi=max(max(a) for a in series)+2
    for value in range(int(lo)//5*5,int(hi)+5,5):
     yy=330-(value-lo)/(hi-lo)*220
     parts.append(f'<path d="M70 {yy} H1040" stroke="#e4e6e8"/><text x="28" y="{yy+5}" font-size="12">{value}</text>')
    for k,color,values in zip(keys,colors,series):
     points=' '.join(f'{70+i*48.5:.1f},{330-(v-lo)/(hi-lo)*220:.1f}' for i,v in enumerate(values))
     parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>')
    for i in [0,5,10,15,20]:parts.append(f'<text x="{60+i*48.5}" y="355" font-size="12">{metrics[keys[0]]["rows"][i][0][5:]}</text>')
    for i,(k,c) in enumerate(zip(keys,colors)):parts.append(f'<text x="{70+i*245}" y="95" fill="{c}" font-size="14">{escape(metrics[k]["name"])} {metrics[k]["twenty_session_pct"]:+.2f}%</text>')
    # Reserve independent columns for names, bars, and numeric labels.
    parts.append('<text x="40" y="405" font-size="17">上一交易日涨跌幅</text>')
    left,right,zero = 300,950,625
    extent = max(1, math.ceil(max(abs(m['daily_pct']) for m in metrics.values())))
    scale = (right-left)/2/extent
    for step in (-1,-0.5,0,0.5,1):
     x = zero + step*extent*scale
     parts.append(f'<path d="M{x} 420 V660" stroke="#cbd2d9" stroke-width="{1.5 if step==0 else 1}"/><text x="{x}" y="680" text-anchor="middle" font-size="12">{step*extent:+g}%</text>')
    for i,(k,m) in enumerate(metrics.items()):
     y=438+i*32;v=m['daily_pct'];width=abs(v)*scale;c='#b45464' if v<0 else '#288b83';x=zero-width if v<0 else zero
     parts.append(f'<text x="40" y="{y+4}" font-size="14">{escape(m["name"])}</text><rect class="daily-bar" x="{x}" y="{y-12}" width="{width}" height="19" fill="{c}"/><text x="1060" y="{y+3}" text-anchor="end" font-size="14">{v:+.2f}%</text>')
    parts.append('<text x="40" y="703" font-size="12">'+('替代收盘报价 + 已存价格指数历史；ETF仅当日报价，区间收益缺失不补画。' if fallback else '来源：腾讯财经日线；指数为价格指数，ETF为接口前复权序列，未视作总回报。')+'</text></g></svg>')
    return ''.join(parts)
