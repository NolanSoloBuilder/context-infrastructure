from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from decimal import Decimal,ROUND_HALF_UP
import pandas as pd
P=Path(__file__).resolve().parent
m={r['symbol']:r for r in json.loads((P/'metrics.json').read_text())}
q=json.loads((P/'quote_verification.json').read_text());ex=json.loads((P/'extended_quotes.json').read_text());wt=json.loads((P/'watchlist_table.json').read_text());g=json.loads((P/'google_update/google_valuation_model.json').read_text())
assert len(m)==27, len(m)
assert all(v['session']=='2026-10-29' for v in m.values())
assert len(wt['rows'])==12 and len({r['symbol'] for r in wt['rows']})==12
assert {r['symbol'] for r in wt['rows'] if r['has_original_drawdown_alert']}=={'QQQ','QQQM','VOO','BRK-B'}
assert all(r['close_match'] for r in q['regular_closes'])
checks=[]
for s in ['QQQM','VOO','BRK-B']:
 d=pd.read_csv(P/f'{s}_daily.csv',index_col='date',parse_dates=True);n=pd.read_csv(P/'normalized_60_sessions.csv',index_col='date',parse_dates=True);tail=d.tail(60)
 assert len(tail)==60 and tail.index.equals(n.index)
 assert abs(n[s].iloc[-1]-tail.close.iloc[-1]/tail.close.iloc[0]*100)<1e-5
 for t,row in tail.iterrows():
  hi=d.loc[(d.index>t-pd.Timedelta(days=364))&(d.index<=t)].high.max();dd=(row.close/hi-1)*100;assert abs(dd-row.drawdown_pct)<1e-5
 assert abs(tail.drawdown_pct.iloc[-1]-m[s]['drawdown_pct'])<1e-5
 checks.append({'symbol':s,'observations':60,'first_date':str(tail.index[0].date()),'last_date':str(tail.index[-1].date()),'normalized_last':float(n[s].iloc[-1]),'drawdown_last_pct':m[s]['drawdown_pct'],'rolling_high_no_lookahead':'passed'})
for s in ['QQQ','QQQM','VOO','BRK-B']:
 for ratio,key in [('.85','level_15'),('.75','level_25')]:
  price=float((Decimal(str(m[s]['high_52w']))*Decimal(ratio)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP));assert price==m[s][key]
assert all(r['post']['minute_volume']==0 for r in ex['observations'])
assert all(r['post']['session']=='2026-10-29' and not r['post']['session_window_ended_at_capture'] for r in ex['observations'])
assert abs(g['scenarios'][1]['price_usd']-216.2809582074652)<1e-7
assert abs(g['scenarios'][1]['asset_bridge_B']-119.6248)<1e-6
assert all((P/f).exists() for f in ['report.md','watchlist_curves.png','sector_daily.png','reddit_digest.md','reddit_sources.json','sofi_research.md','google_update/google_update.md','finews_digest.md'])
report=(P/'report.md').read_text();assert '3万美元' in report and 'QQQM750' in report and '未采用草案' in report
verification={'status':'passed_with_disclosed_gaps','session':'2026-10-29','report_date_beijing':'2026-10-30','verified_at_utc':datetime.now(timezone.utc).isoformat(),'regular_close_cross_checks':q['regular_closes'],'watch_highs':q['watch_high_checks'],'chart_checks':checks,'sector_count':12,'sector_daily_sorted':sorted([{'symbol':s,'day_pct':m[s]['day_pct']} for s in ['XLK','XLC','XLY','XLP','XLV','XLF','XLI','XLE','XLU','XLB','XLRE','SMH']],key=lambda r:r['day_pct'],reverse=True),'ohlc_exception':'XLRE low42.61>open42.43; used cross-checked closes only, not reconstructed low/high/drawdown','extended':'12 zero-volume references; cross-source time/price differences retained; not final postmarket','google_model_checks':'Q3 facts updated, bridge119.6248B and base216.280958 recomputed; forward assumptions not proven','image_visual_inspection':'Both PNGs opened; labels/date/signs/terminal values readable','template_browser_test':'not repeated; unchanged template, file-URL policy restriction respected','gaps':['XLRE OHLC anomaly retained','Broad constituent breadth and index valuation denominator not fully verified','SOFI Q3 full10Q unavailable in latest SEC submission snapshot','Third-party transcript scope, not complete official audio verification','Reddit precise publication times and full24h coverage incomplete','SPX derived reference differs0.17points; common Yahoo sequence retained, no official-close equality asserted'],'no_account_actions':True}
(P/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
print('Verified',len(m),'metrics,12 classified rows,180 no-lookahead points; gaps retained.')
