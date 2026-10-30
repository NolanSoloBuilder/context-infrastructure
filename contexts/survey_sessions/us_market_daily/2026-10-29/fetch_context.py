from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from html.parser import HTMLParser
from pathlib import Path
import subprocess,json,hashlib
OUT=Path(__file__).resolve().parent
class Parse(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.skip=0;self.rows=[];self.row=None;self.cell=None
 def handle_starttag(self,t,a):
  if t in ['script','style']:self.skip+=1
  if t=='tr':self.row=[]
  if t in ['th','td']:self.cell=[]
 def handle_endtag(self,t):
  if t in ['script','style']:self.skip=max(0,self.skip-1)
  if t in ['th','td'] and self.cell is not None:
   if self.row is not None:self.row.append(' '.join(self.cell).strip())
   self.cell=None
  if t=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
  if t in ['p','div','h1','h2','h3','tr','li']:self.parts.append('\n')
 def handle_data(self,s):
  if not self.skip:
   self.parts.append(s)
   if self.cell is not None:self.cell.append(s)
SOURCES={
 'treasury':'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2026',
 'fed':'https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm',
 'bea':'https://www.bea.gov/news/schedule',
 'bls_oct':'https://www.bls.gov/schedule/2026/10_sched.htm',
 'bls_nov':'https://www.bls.gov/schedule/2026/11_sched.htm',
 'nyse':'https://www.nyse.com/trade/hours-calendars',
 'berkshire':'https://www.berkshirehathaway.com/news/2026news.html',
 'msft':'https://news.microsoft.com/source/2026/10/28/microsoft-announces-first-quarter-results-2/',
 'cboe':'https://www.cboe.com/tradable-products/vix/',
 'qqq':'https://stockanalysis.com/etf/qqq/',
 'qqqm':'https://stockanalysis.com/etf/qqqm/',
 'voo':'https://stockanalysis.com/etf/voo/',
 'brkb':'https://stockanalysis.com/stocks/brk.b/',
 'googl_history':'https://stockanalysis.com/stocks/googl/history/',
 'qqq_history':'https://stockanalysis.com/etf/qqq/history/',
 'qqqm_history':'https://stockanalysis.com/etf/qqqm/history/',
 'voo_history':'https://stockanalysis.com/etf/voo/history/',
 'brkb_history':'https://stockanalysis.com/stocks/brk.b/history/',
 'sp500':'https://stockanalysis.com/quote/index/SPX/history/',
 'nasdaq':'https://stockanalysis.com/quote/index/IXIC/history/',
}
def fetch(kv):
 k,url=kv
 try:
  r=subprocess.run(['curl','-sSL','--fail','--max-time','25','-A','Mozilla/5.0',url],capture_output=True,check=True)
  p=OUT/'context_raw'/f'{k}.html';p.write_bytes(r.stdout)
  parser=Parse();parser.feed(r.stdout.decode('utf-8',errors='replace'))
  txt='\n'.join(' '.join(s.split()) for s in ''.join(parser.parts).splitlines() if s.strip())
  p.with_suffix('.txt').write_text(txt)
  if k=='treasury':
   dates=[row for row in parser.rows if row and row[0] in ['10/27/2026','10/28/2026']]
   heads=[row for row in parser.rows if any('2 Yr' in c or '10 Yr' in c for c in row)]
   (OUT/'treasury_rows.json').write_text(json.dumps({'headers':heads,'rows':dates},ensure_ascii=False,indent=2))
   print('treasury',json.dumps({'headers':heads,'rows':dates}))
  return {'key':k,'url':url,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(r.stdout).hexdigest(),'raw_file':str(p.relative_to(OUT)),'read_scope':'HTML public body and tables','status':'fetched'}
 except Exception as e:return {'key':k,'url':url,'status':'failed','error':str(e)}
with ThreadPoolExecutor(max_workers=4) as p:results=list(p.map(fetch,SOURCES.items()))
(OUT/'context_source_manifest.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
print([(r['key'],r['status']) for r in results])
