from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from datetime import datetime,timezone
import json,subprocess,re
P=Path(__file__).resolve().parent
metrics={r['symbol']:r for r in json.loads((P/'metrics.json').read_text())}
seed=json.loads((P.parents[3]/'adhoc_jobs/us_market_site/worker/seed.json').read_text())
assets={a['symbol']:a for g in seed['catalog']['groups'] for a in g['assets']};assets['GOOG']={'kind':'stock'}
class Tables(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None
 def handle_starttag(self,t,a):
  if t=='tr':self.row=[]
  if t in ['td','th'] and self.row is not None:self.cell=''
 def handle_data(self,d):
  if self.cell is not None:self.cell+=d
 def handle_endtag(self,t):
  if t in ['td','th'] and self.cell is not None:self.row.append(self.cell.strip());self.cell=None
  if t=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
raw=P/'crosscheck_raw';raw.mkdir(exist_ok=True)
def work(item):
 s,a=item;slug=s.lower().replace('-','.');kind='etf' if a.get('kind')=='fund' else 'stocks';url=f'https://stockanalysis.com/{kind}/{slug}/history/'
 r=subprocess.run(['curl','--fail','--silent','--show-error','--max-time','25','-A','Mozilla/5.0',url],capture_output=True,text=True)
 record={'symbol':s,'url':url,'captured_at_utc':datetime.now(timezone.utc).isoformat(),'provider':'Stock Analysis (third-party; may share upstream data)'}
 if r.returncode:return {**record,'status':'unavailable','error':r.stderr[:160]}
 (raw/(s+'.html')).write_text(r.stdout);p=Tables();p.feed(r.stdout)
 wanted=[x for x in p.rows if x and x[0]=='Oct 30, 2026']
 if not wanted:return {**record,'status':'missing_dated_history_row','read_scope':'HTTP HTML, no matching dated table row'}
 row=wanted[0];close=float(row[4].replace(',',''));record.update(status='read',date='2026-10-30',row=row,close_usd=close,yahoo_close_usd=metrics[s]['close'],close_match=abs(close-metrics[s]['close'])<.005,read_scope='Dated OHLC table and visible quote header')
 if s in ['QQQM','VOO','BRK-B']:
  highdate=metrics[s]['high_date'];wanteddate=datetime.fromisoformat(highdate).strftime('%b %d, %Y').replace(' 0',' ')
  h=next((x for x in p.rows if x and x[0]==wanteddate),None)
  record['high_check']={'yahoo_high':metrics[s]['high_52w'],'date':highdate,'second_source_daily_high':float(h[2].replace(',','')) if h else None,'scope':'high on claimed maximum date; not independently scanned entire52weeks'}
 # Explicit timestamp in HTML is required for cross-source after-hours.
 text=re.sub('<[^>]+>',' ',r.stdout);text=re.sub(r'\s+',' ',text)
 record['header_excerpt']=text[text.find('At close:')-70:text.find('After-hours:')+90] if 'After-hours:' in text else ''
 return record
with ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(work,assets.items()))
(P/'quote_verification.json').write_text(json.dumps({'session':'2026-10-30','regular_closes':records,'method':'Yahoo daily OHLC compared with dated Stock Analysis historical table; third-party, possibly common upstream; never imply official exchange close audit'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps([{k:x[k] for k in ['symbol','status','close_match','high_check'] if k in x} for x in records],ensure_ascii=False))
