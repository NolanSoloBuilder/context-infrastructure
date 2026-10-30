"""Collect explicit-date market data and charts; reject stale or mixed sessions."""
import argparse
p=argparse.ArgumentParser()
p.add_argument("--report-date",required=True)
p.add_argument("--asof",required=True)
p.add_argument("--quotes-file",help="Reviewed same-session fallback quotes with source URLs; ETF interval returns omitted")
args=p.parse_args()
assert args.asof < args.report_date
import json
from pathlib import Path
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'contexts/survey_sessions/a_share_daily' / args.report_date
OUT.mkdir(parents=True, exist_ok=True)
ASOF = args.asof
SYMBOLS = {'sh000001':'上证指数','sh000016':'上证50','sh000300':'沪深300','sh000688':'科创50','sh510050':'上证50ETF · 510050','sh510300':'沪深300ETF · 510300','sh588000':'科创50ETF · 588000'}

def fetch(symbol):
    if args.quotes_file:
        q=json.loads(Path(args.quotes_file).read_text())
        assert q['asof']==ASOF
        a=q['metrics'][symbol]
        assert a['session']==ASOF and a['source'].startswith('https://')
        if symbol in list(SYMBOLS)[:4]:
            hist=Path(q['history_directory'])/f'{symbol}_raw.json'
            prior=json.loads(hist.read_text())['data'][symbol]['day']
            assert prior[-1][0]==q['history_asof'] and prior[-1][0]<ASOF
            assert float(prior[-1][2])==a['previous_close']
            rows=prior+[[ASOF,None,str(a['close']),None,None,None]]
            interval=(a['close']/float(rows[-21][2])-1)*100
            raw={'data':{symbol:{'day':rows}},'provenance':{'historical_file':str(hist),'current_quote':a,'method':'历史价格指数收盘加已审核同一指数当日收盘，未生成开高低或成交量'}}
            (OUT/f'{symbol}_raw.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2))
        else:
            rows=[];interval=None
        return symbol, {'name':SYMBOLS[symbol],'source':a['source'],'price_basis':'price_index_mixed_source' if rows else 'unadjusted_spot_quote','session':ASOF,'close':a['close'],'daily_pct':a['daily_pct'],'twenty_session_pct':interval,'rows':rows[-21:],'quote_precision_decimals':a.get('precision',2),'fallback':True}
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
(OUT/'market.json').write_text(json.dumps({'collected_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'asof':ASOF,'provider':'审核后的替代收盘报价及已存历史价格指数' if args.quotes_file else '腾讯财经公开行情；第三方数据','metrics':metrics},ensure_ascii=False,indent=2))
# Standalone SVG keeps daily collection independent of plotting installations.
from html import escape
w,h=1100,730
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="#fff"/><g font-family="Arial, PingFang SC, sans-serif" fill="#24323d">',f'<text x="40" y="38" font-size="23">指数与ETF · {ASOF} 收盘</text>', '<text x="40" y="70" font-size="15">近20交易日指数价格表现 · 起点100</text>']
keys=list(SYMBOLS)[:4];colors=['#247c91','#6674d6','#cc9136','#b15280']
series=[[float(r[2])/float(metrics[k]['rows'][0][2])*100 for r in metrics[k]['rows']] for k in keys]
lo=min(min(a) for a in series)-2;hi=max(max(a) for a in series)+2
for value in range(int(lo)//5*5,int(hi)+5,5):
 yy=330-(value-lo)/(hi-lo)*220
 parts.append(f'<path d="M70 {yy} H1040" stroke="#e4e6e8"/><text x="28" y="{yy+5}" font-size="12">{value}</text>')
for k,color,values in zip(keys,colors,series):
 points=' '.join(f'{70+i*48.5:.1f},{330-(v-lo)/(hi-lo)*220:.1f}' for i,v in enumerate(values))
 parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>')
for i in [0,5,10,15,20]:parts.append(f'<text x="{60+i*48.5}" y="355" font-size="12">{metrics[keys[0]]["rows"][i][0][5:]}</text>')
for i,(k,c) in enumerate(zip(keys,colors)):parts.append(f'<text x="{70+i*245}" y="95" fill="{c}" font-size="14">{escape(SYMBOLS[k])} {metrics[k]["twenty_session_pct"]:+.2f}%</text>')
parts.append('<text x="40" y="405" font-size="17">上一交易日涨跌幅</text>')
for i,(k,m) in enumerate(metrics.items()):
 y=438+i*32;v=m['daily_pct'];width=abs(v)*110;c='#b45464' if v<0 else '#288b83';x=600-width if v<0 else 600
 parts.append(f'<text x="40" y="{y+4}" font-size="14">{escape(m["name"])}</text><rect x="{x}" y="{y-12}" width="{width}" height="19" fill="{c}"/><text x="{max(620,x+width+12)}" y="{y+3}" font-size="14">{v:+.2f}%</text>')
parts.append('<text x="40" y="703" font-size="12">'+('替代收盘报价 + 已存价格指数历史；ETF仅当日报价，区间收益缺失不补画。' if args.quotes_file else '来源：腾讯财经日线；指数为价格指数，ETF为接口前复权序列，未视作总回报。')+'</text></g></svg>')
(OUT/'market.svg').write_text(''.join(parts))
print(json.dumps({k:{x:v for x,v in m.items() if x!='rows'} for k,m in metrics.items()},ensure_ascii=False))

trend={}
for symbol in list(SYMBOLS)[:4]:
 data=json.loads((OUT/f'{symbol}_raw.json').read_text())['data'][symbol]
 rows=[r for r in data['day'] if r[0]<=ASOF]
 assert len(rows)>=60
 ma=sum(float(r[2]) for r in rows[-60:])/60
 trend[symbol]={'name':SYMBOLS[symbol],'asof':ASOF,'close':float(rows[-1][2]),'ma60':ma,'gap_pct':(float(rows[-1][2])/ma-1)*100,'source':metrics[symbol]['source'],'method':('最近60交易日价格指数收盘算术平均；历史来自审核JSON指定存档，最新收盘来自该JSON来源，前收盘一致性检查通过' if args.quotes_file else '最近60个交易日指数收盘算术平均')}
(OUT/'trend_metrics.json').write_text(json.dumps(trend,ensure_ascii=False,indent=2))
