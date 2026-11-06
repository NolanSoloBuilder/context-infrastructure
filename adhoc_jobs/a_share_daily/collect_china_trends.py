"""Add a separate overseas-China watchlist without changing A-share decision state."""
import argparse,json,subprocess,math
from pathlib import Path
from datetime import datetime,time
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor
p=argparse.ArgumentParser();p.add_argument('--report-dir',required=True);p.add_argument('--cutoff',help='Timezone-aware report observation cutoff; default report day 09:00 Beijing');p.add_argument('--a-history-endpoint',default='https://web.ifzq.gtimg.cn/appstock/app/fqkline/get',choices=['https://web.ifzq.gtimg.cn/appstock/app/fqkline/get','https://proxy.finance.qq.com/ifzqgtimg/appstock/app/fqkline/get']);a=p.parse_args()
out=Path(a.report_dir);data=json.loads((out/'trends.json').read_text());report_date=out.name
cutoff=datetime.fromisoformat(a.cutoff) if a.cutoff else datetime.fromisoformat(report_date+'T09:00:00+08:00');assert cutoff.tzinfo
config=json.loads(Path(__file__).with_name('china_watchlist.json').read_text());rawdir=out/'sources/china_trend_history';rawdir.mkdir(parents=True,exist_ok=True)
def fetch(item):
 symbol=item['symbol'];zone=ZoneInfo(item['timezone']);end=cutoff.astimezone(zone).date().isoformat();start=f'{int(end[:4])-4}{end[4:]}'
 endpoint=f'https://web.ifzq.gtimg.cn/appstock/app/{item["endpoint"]}/get' if symbol.startswith('us') else a.a_history_endpoint
 url=f'{endpoint}?param={symbol},day,{start},{end},1000,qfq'
 body=subprocess.check_output(['curl','--fail','--silent','--show-error','--max-time','30',url],text=True);d=json.loads(body)['data'][symbol];key='qfqday' if 'qfqday' in d else 'day'
 close_hour=16 if symbol.startswith('us') else 15
 rows=[r for r in d[key] if datetime.combine(datetime.fromisoformat(r[0]).date(),time(close_hour),zone)<cutoff]
 assert len(rows)>=21 and rows==sorted(rows,key=lambda r:r[0])
 assert len({r[0] for r in rows})==len(rows)
 last=rows[-1][0];points=[];closes=[]
 for r in rows:
  v=float(r[2]);assert math.isfinite(v) and v>0;closes.append(v)
  points.append(dict(date=r[0],close=v,ma20=sum(closes[-20:])/20 if len(closes)>=20 else None,ma60=sum(closes[-60:])/60 if len(closes)>=60 else None))
 qt=d.get('qt',{}).get(symbol,[]);crosscheck='未获同日期即时报价，历史日线为单一提供方'
 if len(qt)>30 and str(qt[30]).startswith(last):
  assert abs(float(qt[3])-closes[-1])<max(.002,closes[-1]*.0001),(symbol,'history/quote mismatch')
  crosscheck='历史最后收盘与同一提供方同日期报价一致；非独立跨源核验'
 gap=None
 if len(qt)>30:
  stamp=str(qt[30])[:19]
  try:quote_time=datetime.strptime(stamp,'%Y-%m-%d %H:%M:%S').replace(tzinfo=zone)
  except ValueError:quote_time=None
  if quote_time and quote_time<cutoff and quote_time.date().isoformat()>last and quote_time.time()>=time(close_hour):
   gap=dict(symbol=symbol,history_asof=last,missing_session=quote_time.date().isoformat(),quote_time=quote_time.isoformat(),reason='提供方收盘后报价日期比历史末日更新，未用点价拼接复权日线')
   crosscheck+=f'；历史仅至{last}，缺{gap["missing_session"]}已完成日线'
 (rawdir/f'{symbol.replace(".","_")}.json').write_text(body)
 asset={k:v for k,v in item.items() if k not in ['endpoint','timezone']};asset.update(group='china',source=url,first_date=rows[0][0],asof=last,points=points,basis='前复权价格，非完整含分红总回报' if key=='qfqday' else '日收盘价格，未验证复权',quality=crosscheck,history_gap=gap)
 return symbol,asset
assets={};failures=[]
with ThreadPoolExecutor(max_workers=4) as pool:
 futures=[(item,pool.submit(fetch,item)) for item in config]
 for item,f in futures:
  try:s,v=f.result();assets[s]=v
  except Exception as e:failures.append(dict(symbol=item['symbol'],error=str(e)))
# Replace just this group; a partial failure never masquerades as full coverage.
data['assets']={s:v for s,v in data['assets'].items() if v.get('group')!='china'};data['assets'].update(assets)
data['china_watchlist']=dict(cutoff=cutoff.isoformat(),count=len(assets),expected=len(config),failures=failures,stale_histories=[a['history_gap'] for a in assets.values() if a.get('history_gap')],provider='腾讯财经海外日线；各标的独立日期；单一提供方')
(out/'trends.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
(out/'sources/china_trend_audit.json').write_text(json.dumps(data['china_watchlist'],ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(assets={s:dict(rows=len(v['points']),asof=v['asof'],close=v['points'][-1]['close']) for s,v in assets.items()},failures=failures),ensure_ascii=False))
if not assets:raise SystemExit('No overseas-China history verified')
