from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from html.parser import HTMLParser
import subprocess,json,hashlib
P=Path(__file__).resolve().parent
S={'stockanalysis':'https://stockanalysis.com/stocks/googl/transcripts/712854-q3-2026/','benzinga':'https://www.benzinga.com/news/26/10/62679903/alphabet-q3-2026-earnings-call-transcript','fool':'https://www.fool.com/earnings/call-transcripts/2026/10/29/alphabet-googl-q3-2026-earnings-call-transcript/','official_ceo':'https://blog.google/company-news/inside-google/message-ceo/alphabet-earnings-q3-2026/'}
class Parse(HTMLParser):
 def __init__(self):super().__init__();self.text=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ['script','style']:self.skip+=1
 def handle_endtag(self,t):
  if t in ['script','style']:self.skip=max(0,self.skip-1)
  if t in ['p','div','li','h1','h2','h3','tr']:self.text.append('\n')
 def handle_data(self,s):
  if not self.skip:self.text.append(s)
def f(kv):
 k,url=kv
 try:
  r=subprocess.run(['curl','-sSL','--fail','--max-time','20','-A','Mozilla/5.0',url],check=True,capture_output=True)
  parser=Parse();parser.feed(r.stdout.decode(errors='replace'));text='\n'.join(' '.join(x.split()) for x in ''.join(parser.text).splitlines() if x.strip())
  (P/'raw'/f'{k}.html').write_bytes(r.stdout);(P/'raw'/f'{k}.txt').write_text(text)
  return {'id':k,'url':url,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(r.stdout).hexdigest(),'status':'archived_public_body','raw_file':f'raw/{k}.html'}
 except Exception as ex:return {'id':k,'url':url,'status':'CLI_archive_failed_web_body_read_separately','error':str(ex)}
with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(f,S.items()))
(P/'archive_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print([(r['id'],r['status']) for r in rows])
