"""Collect explicit-date market data and charts; reject stale or mixed sessions."""
import argparse
p=argparse.ArgumentParser()
p.add_argument("--report-date",required=True)
p.add_argument("--asof",required=True)
p.add_argument("--history-endpoint",default="https://web.ifzq.gtimg.cn/appstock/app/fqkline/get",choices=["https://web.ifzq.gtimg.cn/appstock/app/fqkline/get","https://proxy.finance.qq.com/ifzqgtimg/appstock/app/fqkline/get"],help="Explicit Tencent history route; actual URL retained in each quote")
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
    url = f'{args.history_endpoint}?param={symbol},day,,,80,qfq'
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
# Rendering is reusable so chart fixes do not refetch or mutate quotes.
from market_chart import render_market_svg
(OUT/'market.svg').write_text(render_market_svg(metrics, ASOF, bool(args.quotes_file)))
print(json.dumps({k:{x:v for x,v in m.items() if x!='rows'} for k,m in metrics.items()},ensure_ascii=False))

trend={}
for symbol in list(SYMBOLS)[:4]:
 data=json.loads((OUT/f'{symbol}_raw.json').read_text())['data'][symbol]
 rows=[r for r in data['day'] if r[0]<=ASOF]
 assert len(rows)>=60
 ma=sum(float(r[2]) for r in rows[-60:])/60
 trend[symbol]={'name':SYMBOLS[symbol],'asof':ASOF,'close':float(rows[-1][2]),'ma60':ma,'gap_pct':(float(rows[-1][2])/ma-1)*100,'source':metrics[symbol]['source'],'method':('最近60交易日价格指数收盘算术平均；历史来自审核JSON指定存档，最新收盘来自该JSON来源，前收盘一致性检查通过' if args.quotes_file else '最近60个交易日指数收盘算术平均')}
(OUT/'trend_metrics.json').write_text(json.dumps(trend,ensure_ascii=False,indent=2))
