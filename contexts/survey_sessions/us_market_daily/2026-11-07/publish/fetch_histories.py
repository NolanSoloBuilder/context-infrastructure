import json,subprocess,concurrent.futures,datetime
from pathlib import Path
from urllib.parse import quote
base=Path(__file__).parent
raw=base/'market_raw';raw.mkdir(exist_ok=True)
seed=json.loads(Path('adhoc_jobs/us_market_site/worker/seed.json').read_text())
symbols=[a['symbol'] for g in seed['catalog']['groups'] for a in g['assets']]
symbols=list(dict.fromkeys(symbols+'NOW CRM GEHC PLTR ACN EPAM GLOB TEM ISRG IGV XSW IHI BOTZ AIQ SKHY SPCX TSLA AAPL BA'.split()))
def get(s):
 url=f'https://query1.finance.yahoo.com/v8/finance/chart/{quote(s,safe="")}?range={"1mo" if s=="^GSPC" else "5y"}&interval=1d&events=div%2Csplits&includeAdjustedClose=true'
 at=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(['curl','-fsS','--max-time','18','-A','Mozilla/5.0',url],capture_output=True,text=True)
 try:
  d=json.loads(p.stdout);r=d['chart']['result'][0];assert r['meta']['symbol']==s
  (raw/f'{s}.json').write_text(p.stdout);return {'symbol':s,'status':'ok','url':url,'captured_at':at,'name':r['meta'].get('longName',r['meta'].get('shortName')),'currency':r['meta']['currency'],'bars':len(r.get('timestamp',[]))}
 except Exception as e:return {'symbol':s,'status':'error','url':url,'captured_at':at,'error':str(e),'http_error':p.stderr[:200]}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: rows=list(pool.map(get,['^GSPC']+symbols))
(base/'market_collection.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(rows,ensure_ascii=False))
