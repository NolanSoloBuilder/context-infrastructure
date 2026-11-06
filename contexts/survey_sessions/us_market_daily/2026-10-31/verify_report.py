from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from decimal import Decimal,ROUND_HALF_UP
import pandas as pd
P=Path(__file__).resolve().parent;m={r['symbol']:r for r in json.loads((P/'metrics.json').read_text())};q=json.loads((P/'quote_verification.json').read_text());wt=json.loads((P/'watchlist_table.json').read_text());ex=json.loads((P/'extended_quotes.json').read_text());report=(P/'report.md').read_text()
assert len(m)==33 and all(r['session']=='2026-10-30' for r in m.values());assert len(wt['rows'])==17 and len({r['symbol'] for r in wt['rows']})==17
assert 'QQQ' not in m and all(r['symbol']!='QQQ' for r in wt['rows']);assert {r['symbol'] for r in wt['rows'] if r['has_original_drawdown_alert']}=={'QQQM','VOO','BRK-B'}
assert len(q['regular_closes'])==18 and all(r['close_match'] for r in q['regular_closes'])
normalized=pd.read_csv(P/'normalized_60_sessions.csv',index_col='date',parse_dates=True);checks=[]
for s in ['QQQM','VOO','BRK-B']:
 d=pd.read_csv(P/f'{s}_daily.csv',index_col='date',parse_dates=True);tail=d.tail(60);assert tail.index.equals(normalized.index)
 assert abs(normalized[s].iloc[-1]-tail.close.iloc[-1]/tail.close.iloc[0]*100)<1e-5
 for t,r in tail.iterrows():
  hi=d.loc[(d.index>t-pd.Timedelta(days=364))&(d.index<=t)].high.max();assert abs((r.close/hi-1)*100-r.drawdown_pct)<1e-5
 for factor,key in [('.85','level_15'),('.75','level_25')]:assert float((Decimal(str(m[s]['high_52w']))*Decimal(factor)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))==m[s][key]
 checks.append({'symbol':s,'daily_points':60,'start':str(tail.index[0].date()),'end':str(tail.index[-1].date()),'normalized_end':float(normalized[s].iloc[-1]),'drawdown_end_pct':m[s]['drawdown_pct'],'no_lookahead':True})
assert m['DRAM']['ma200'] is None and m['DRAM']['high_52w'] is None
assert len(ex['observations'])==18 and all(r['post']['session']=='2026-10-30' for r in ex['observations']);assert all(not r['post']['bar_has_positive_volume'] for r in ex['observations']);assert all(not r['post']['session_window_ended_at_capture'] for r in ex['observations'])
assert '已有VOO／QQQM／GOOG仓位' in report and '未重新登录嘉信' in report and '基线均价' in report and 'QQQ已从当前清单移除' in report
for file in ['watchlist_curves.png','sector_daily.png','reddit_digest.md','reddit_sources.json','finews_digest.md','macro_research.md']:assert (P/file).exists()
verification={'status':'passed_with_disclosed_gaps','session':'2026-10-30','report_date_beijing':'2026-10-31','checked_at_utc':datetime.now(timezone.utc).isoformat(),'regular_closes_crosschecked':18,'regular_metrics_count':33,'watchlist_count':17,'chart_checks':checks,'chart_visual_check':'both PNGs opened; date/signs/Chinese/terminal values readable','alerts':'QQQM andVOO eligible for update, no new tier; BRK.B high discrepancy deferred and last valid state preserved','high_discrepancies':{'QQQM':'314.11 Yahoo /314.12 StockAnalysis, disclosed','BRK.B':'550.30 Yahoo /550.47 StockAnalysis, defer persistent high/threshold update'},'holdings':'2026-10-30 authorized local baseline; no broker login or quantity refresh; actualGOOG distinct from researchGOOGL','gaps':['BRK.B exact high unresolved','Reddit24hour scan incomplete; RSS403; original absolute timestamp missing','index valuation denominator and full constituent breadth unverified','SoFiQ3full10Q not yet in currentSEC list','GoogleTPU standalone hardware/service margins absent','automatic quote sources may share upstream; not official exchange tick audit'],'report_sha256':hashlib.sha256(report.encode()).hexdigest(),'no_orders':True,'public_site_untouched':True}
(P/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n');print('Verified33metrics/18cross-checked closes/17watch rows/180point rolling highs; BRK high deferred')
