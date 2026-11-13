from pathlib import Path
import json,subprocess,hashlib,concurrent.futures
from datetime import datetime,timezone
from html.parser import HTMLParser
P=Path(__file__).resolve().parent/'market_crosscheck_raw';P.mkdir(exist_ok=True)
class Clean(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.parts=[]
 def handle_starttag(self,tag,attrs):
  if tag in ('script','style'):self.skip+=1
 def handle_endtag(self,tag):
  if tag in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip and d.strip():self.parts.append(d.strip())
def run(s):
 u='https://stockanalysis.com/'+('etf/' if s in ['qqqm','voo'] else 'stocks/')+s+'/history/'
 now=datetime.now(timezone.utc).isoformat()
 r=subprocess.run(['curl','-fsSL','--max-time','30',u],capture_output=True)
 if r.returncode:return {'symbol':s,'url':u,'retrieved_at':now,'error':r.stderr.decode()}
 (P/(s+'.html')).write_bytes(r.stdout);c=Clean();c.feed(r.stdout.decode());txt='\n'.join(c.parts);(P/(s+'.txt')).write_text(txt)
 return {'symbol':s,'url':u,'retrieved_at':now,'sha256':hashlib.sha256(r.stdout).hexdigest(),'bytes':len(r.stdout)}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(run,['qqqm','voo','brk.b','nvda','googl','sofi','now','crm','gehc','cgnx']))
(P/'manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print(json.dumps(rows,ensure_ascii=False))
