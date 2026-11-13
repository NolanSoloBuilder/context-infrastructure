from pathlib import Path
import concurrent.futures, subprocess, json
from datetime import datetime, timezone
from html.parser import HTMLParser
OUT=Path(__file__).parent / "macro_raw"
OUT.mkdir(parents=True,exist_ok=True)
SOURCES={
"bls_cpi_schedule":"https://www.bls.gov/schedule/news_release/cpi.htm",
"fed_nov_calendar":"https://www.federalreserve.gov/newsevents/2026-november.htm",
"bls_schedule_nov":"https://www.bls.gov/schedule/2026/11_sched.htm",
"bls_jobs_schedule":"https://www.bls.gov/schedule/news_release/empsit.htm",
"treasury":"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value=202611&type=daily_treasury_yield_curve",
"cboe_vix":"https://www.cboe.com/tradable-products/vix",
"cboe_vix_history":"https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv",
"wsj_vix":"https://www.wsj.com/market-data/quotes/index/VIX/historical-prices",
"nyse_calendar":"https://www.nyse.com/trade/hours-calendars",
"sifma_calendar":"https://www.sifma.org/resources/general/holiday-schedule/",
"fomc_calendar":"https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
"dol_claims_schedule":"https://oui.doleta.gov/unemploy/claims_arch.asp",
"sgov":"https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf",
"csco_calendar":"https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2026/m11/cisco-schedules-conference-call-for-q1-fiscal-year-2027-financial-results.html",
"amat_calendar":"https://ir.appliedmaterials.com/news-releases/news-release-details/applied-materials-report-fourth-quarter-and-fiscal-2026-results",
"nvda_calendar":"https://nvidianews.nvidia.com/news/nvidia-sets-conference-call-for-third-quarter-financial-results-6928873",
"mrna_sec_calendar":"https://www.sec.gov/Archives/edgar/data/1682852/000168285226000194/exhibit9912026q3pressrelea.htm",
"mrna_events":"https://investors.modernatx.com/events-presentations"}
class Text(HTMLParser):
 def __init__(self): super().__init__(); self.parts=[];self.ignore=0
 def handle_starttag(self,t,a):
  if t in ("script","style"): self.ignore+=1
 def handle_endtag(self,t):
  if t in ("script","style"): self.ignore=max(0,self.ignore-1)
 def handle_data(self,d):
  if not self.ignore and d.strip():self.parts.append(d.strip())
def get(item):
 k,u=item; ext=".csv" if u.endswith(".csv") else ".html"
 p=OUT/(k+ext); start=datetime.now(timezone.utc).isoformat()
 r=subprocess.run(["curl","-L","--max-time","35","--connect-timeout","12","-sS","-w","%{http_code}","-o",str(p),u],capture_output=True,text=True)
 receipt={"id":k,"url":u,"retrieved_at_utc":start,"http_status":r.stdout,"exit_code":r.returncode,"error":r.stderr,"file":str(p.relative_to(Path(__file__).parent))}
 if p.exists():
  receipt["bytes"]=p.stat().st_size
  if ext==".html":
   parser=Text();parser.feed(p.read_text(errors="replace"));(OUT/(k+".txt")).write_text("\n".join(parser.parts))
 return receipt
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(get,SOURCES.items()))
(OUT/"http_receipts.json").write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps([{k:r.get(k) for k in ["id","http_status","exit_code","bytes","error"]}for r in results],ensure_ascii=False))

