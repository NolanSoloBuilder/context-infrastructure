from pathlib import Path
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
import json,re
P=Path(__file__).resolve().parent;m={r['symbol']:r for r in json.loads((P/'metrics.json').read_text())};now=datetime.now(timezone.utc).isoformat()
http=json.loads((P/'quote_verification.json').read_text());(P/'quote_http_attempts.json').write_text(json.dumps(http,ensure_ascii=False,indent=2))
text=(P/'crosscheck_web.txt').read_text()+'\n'+(P/'crosscheck_web_extra.txt').read_text();records={};ext=json.loads((P/'extended_quotes.json').read_text());quotes={x['symbol']:x for x in ext['observations']};comp=[]
for block in re.split(r'(?=^[^\n]+ \(https://stockanalysis\.com/)',text,flags=re.M):
 url=re.search(r'\((https://stockanalysis.com/(?:stocks|etf)/([^/]+)/history/)\)',block)
 if not url:continue
 s=url[2].upper().replace('BRK.B','BRK-B');body=re.sub(r'^L\d+: ?', '',block, flags=re.M)
 line=next((x for x in body.splitlines() if x.startswith('Oct 30, 2026  |')),None)
 if not line:continue
 row=[x.strip() for x in line.split('|')];close=float(row[4].replace(',',''));record={'symbol':s,'url':url[1],'method':'web reader public page text; direct HTTP403 retained separately, no login or bypass','session':'2026-10-30','row':row,'close_usd':close,'yahoo_close_usd':m[s]['close'],'close_match':abs(close-m[s]['close'])<.005,'captured_at_utc':now}
 if s in ['QQQM','VOO','BRK-B']:
  date=m[s]['high_date'];fmt=datetime.fromisoformat(date).strftime('%b %d, %Y').replace(' 0',' ');h=next((x for x in body.splitlines() if x.startswith(fmt+'  |')),None)
  record['high_check']={'yahoo_high':m[s]['high_52w'],'date':date,'second_source_high':float(h.split('|')[2].replace(',','')) if h else None,'entire52week_secondary_scan':False}
 records[s]=record
 match=re.search(r'At close:[^\n]+\n+\s*([\d,.]+)\n+[\s\S]*?After-hours:\s*Oct 30, 2026, (\d+):(\d+) (AM|PM) EDT',body)
 if match and s in quotes:
  hour=int(match[2])%12+(12 if match[4]=='PM' else 0);stamp=datetime(2026,10,30,hour,int(match[3]),tzinfo=ZoneInfo('America/New_York'));price=float(match[1].replace(',',''));y=quotes[s].get('post',{})
  comp.append({'symbol':s,'regular_close_usd':close,'stockanalysis_price_usd':price,'stockanalysis_time_et':stamp.isoformat(),'stockanalysis_time_beijing':stamp.astimezone(ZoneInfo('Asia/Shanghai')).isoformat(),'source_url':url[1],'yahoo_price_usd':y.get('price_usd'),'yahoo_time_beijing':y.get('bar_start_beijing'),'note':'Different quote timestamps; no assertion of same trade or executable price; Yahoo zero-volume minute reference'})
assert len(records)==18,(len(records),records.keys());assert all(r['close_match'] for r in records.values())
verification={'session':'2026-10-30','regular_closes':list(records.values()),'sources':'YahooOHLC and third-party StockAnalysis; common upstream possible; not an official exchange audit','highs_warning':'QQQM314.11 vs314.12; BRK.B550.30 vs550.47; unverified BRK new high not committed to persistent alert state'}
(P/'quote_verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n');(P/'extended_verification.json').write_text(json.dumps({'quote_session_us':'2026-10-30','comparisons':comp,'display':'retain Yahoo same-source references, show dated source differences; no override','captured_at_utc':now},ensure_ascii=False,indent=2)+'\n')
lines=['# 盘前盘后来源与时段详情','',f"本次Yahoo采集：{ext['observations'][0]['captured_at_utc']}（UTC）。报价单位USD；下个美股交易日11/2盘前尚未开始。下表是10/30历史盘前及10/30盘后快照，不能把历史盘前冒称11/2。盘后采集时19:29EDT仍在交易，非最终盘后收盘。所有分钟参考均零量，不证明新成交。",'','|标的|10/30历史盘前／北京时间|10/30盘后／北京时间|','|---|---|---|']
for s,q in quotes.items():
 def fmt(x):return f"{x['price_usd']:.2f} · {x['bar_start_beijing']}" if x.get('status')=='available' else '缺失'
 lines.append(f"|{s}|{fmt(q.get('pre',{}))}|{fmt(q.get('post',{}))}|")
lines+=['','## 第二来源（时刻不同，保留差异）','','|标的|StockAnalysis／北京时间|Yahoo／北京时间|','|---|---|---|']
for c in comp:lines.append(f"|{c['symbol']}|[{c['stockanalysis_price_usd']:.2f}]({c['source_url']}) · {c['stockanalysis_time_beijing']}|{c['yahoo_price_usd']} · {c['yahoo_time_beijing']}|")
(P/'extended_detail.md').write_text('\n'.join(lines)+'\n')
print('crosschecked',len(records),'dated closes;',len(comp),'explicit after-hours source comparisons')
