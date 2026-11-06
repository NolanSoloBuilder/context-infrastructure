"""Collect historical curves for the report's effective session; no live quote substitution."""
import argparse,json,subprocess,math
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import date,datetime
from zoneinfo import ZoneInfo
p=argparse.ArgumentParser();p.add_argument('--report-dir',required=True);p.add_argument('--history-endpoint',default='https://web.ifzq.gtimg.cn/appstock/app/fqkline/get',choices=['https://web.ifzq.gtimg.cn/appstock/app/fqkline/get','https://proxy.finance.qq.com/ifzqgtimg/appstock/app/fqkline/get']);a=p.parse_args()
out=Path(a.report_dir);market=json.loads((out/'market.json').read_text());asof=market['asof']
start=f'{int(asof[:4])-4}{asof[4:]}'
rawdir=out/'sources/trend_history';rawdir.mkdir(parents=True,exist_ok=True)
def fetch(entry):
 symbol,quote=entry
 url=f'{a.history_endpoint}?param={symbol},day,{start},{asof},1000,qfq'
 body=subprocess.check_output(['curl','--fail','--silent','--show-error','--max-time','30',url],text=True)
 data=json.loads(body)['data'][symbol];key='qfqday' if 'qfqday' in data else 'day'
 rows=[r for r in data[key] if r[0]<=asof];assert len(rows)>1 and rows[-1][0]==asof
 assert len({r[0] for r in rows})==len(rows) and rows==sorted(rows,key=lambda r:r[0])
 assert abs(float(rows[-1][2])-quote['close'])<0.0011,(symbol,'close mismatch')
 archived={r[0]:float(r[2]) for r in quote['rows']}
 assert all(abs(float(r[2])-archived[r[0]])<0.0011 for r in rows if r[0] in archived),(symbol,'overlap mismatch')
 points=[];closes=[]
 for r in rows:
  v=float(r[2]);assert math.isfinite(v) and v>0
  closes.append(v);points.append(dict(date=r[0],close=v,ma20=sum(closes[-20:])/20 if len(closes)>=20 else None,ma60=sum(closes[-60:])/60 if len(closes)>=60 else None))
 (rawdir/f'{symbol}.json').write_text(body)
 return symbol,dict(name=quote['name'],unit='元' if symbol[2:] in ['510050','510300','588000'] else '点',basis='前复权价格，非完整含分红总回报' if key=='qfqday' else '价格指数',source=url,first_date=rows[0][0],asof=asof,points=points)
with ThreadPoolExecutor(max_workers=4) as pool:assets=dict(pool.map(fetch,market['metrics'].items()))
result=dict(asof=asof,collected_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),provider='腾讯财经历史日线；与晨报已核验快照重叠区间逐日比对',assets=assets)
(out/'trends.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
print(json.dumps({k:dict(count=len(v['points']),first=v['first_date'],last=v['asof']) for k,v in assets.items()}))
