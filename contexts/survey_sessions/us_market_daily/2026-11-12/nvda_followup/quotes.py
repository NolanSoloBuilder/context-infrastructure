import sys,json,concurrent.futures,subprocess,hashlib
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path('adhoc_jobs/us_market_daily').resolve()))
from collect_extended import collect_symbol
P=Path(__file__).resolve().parent;raw=P/'quote_raw';raw.mkdir(exist_ok=True);now=datetime.now(timezone.utc)
def run(s):return collect_symbol(s,P.parent,'2026-11-11',now,raw)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(run,['NVDA','QQQM','SMH','SOXX','GOOGL','GOOG']))
(P/'quotes.json').write_text(json.dumps({'captured_at_utc':now.isoformat(),'observations':rows},ensure_ascii=False,indent=2))
for v in rows:print(v['symbol'],v.get('post'))
