from pathlib import Path
from datetime import datetime,timezone
from decimal import Decimal,ROUND_HALF_UP
import json,hashlib,math
import pandas as pd
P=Path(__file__).resolve().parent
metrics=json.loads((P/'metrics.json').read_text());m={x['symbol']:x for x in metrics}
expected={'QQQ':725.61,'QQQM':298.71,'VOO':709.90,'BRK-B':540.34,'GOOGL':324.89}
second_high={'QQQ':762.86,'QQQM':314.12,'VOO':718.47,'BRK-B':549.96}
second_volume={'QQQ':30274641,'QQQM':2425566,'VOO':4773489,'BRK-B':3291100,'GOOGL':62012606}
closes=[]
for s,v in expected.items():
 assert m[s]['close']==v,(s,m[s]['close'],v)
 path='stocks/'+('brk.b' if s=='BRK-B' else s.lower()) if s in ['BRK-B','GOOGL'] else 'etf/'+s.lower()
 closes.append({'symbol':s,'regular_session':'2026-10-28','primary_close_usd':m[s]['close'],'second_close_usd':v,'source_url':f'https://stockanalysis.com/{path}/history/','read_via':'web public body and dated table; CLI raw copy failed','volume_primary':m[s]['volume'],'volume_secondary':second_volume[s],'volume_difference_pct':(m[s]['volume']/second_volume[s]-1)*100})
hi=[]
for s in second_high:
 r=m[s];assert abs(r['high_52w']-second_high[s])<.011
 df=pd.read_csv(P/f'{s}_daily.csv',index_col='date',parse_dates=True)
 w=df.loc[df.index>pd.Timestamp('2026-10-28')-pd.Timedelta(days=364)]
 assert str(w.high.idxmax().date())==r['high_date']
 for factor,key in [('.85','level_15'),('.75','level_25')]:
  value=float((Decimal(str(r['high_52w']))*Decimal(factor)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP));assert value==r[key]
 hi.append({'symbol':s,'primary_high':r['high_52w'],'second_high':second_high[s],'date':r['high_date'],'secondary_high_date_matched_in_dated_history':True,'difference_disclosed':s=='QQQM'})
normalized=pd.read_csv(P/'normalized_60_sessions.csv',index_col=0)
points=0
for s in ['QQQM','VOO','BRK-B']:
 df=pd.read_csv(P/f'{s}_daily.csv',index_col='date',parse_dates=True);tail=df.tail(60)
 assert len(tail)==60 and str(tail.index[-1].date())=='2026-10-28'
 for d,row in tail.iterrows():
  w=df.loc[(df.index<=d)&(df.index>d-pd.Timedelta(days=364))]
  dd=(row.close/w.high.max()-1)*100
  assert abs(dd-row.drawdown_pct)<1e-7
  points+=1
 assert abs(tail.close.iloc[-1]/tail.close.iloc[0]*100-float(normalized[s].iloc[-1]))<1e-6
 assert abs(tail.drawdown_pct.iloc[-1]-m[s]['drawdown_pct'])<1e-7
v={'status':'passed_with_disclosed_gaps','session':'2026-10-28','verified_at_utc':datetime.now(timezone.utc).isoformat(),'watchlist_and_google_closes':closes,'highs':hi,'historical_drawdown_points_recomputed_without_lookahead':points,'normalized_last_values':{s:float(normalized[s].iloc[-1]) for s in ['QQQM','VOO','BRK-B']},'chart_images_read_visually':True,'chart_readability':'Chinese labels, signed values, dates and axes readable; two images checked','original_watch_contract_only':['QQQ','QQQM','VOO','BRK.B'],'indices_second_source':{'SP500':{'close':7743.98,'url':'https://apnews.com/article/7864eac2e13db75f07758ed9c39ad96b'},'IXIC':{'close':26549.85,'url':'https://apnews.com/article/7864eac2e13db75f07758ed9c39ad96b'},'NDX':{'close':29813.16,'url':'https://ca.investing.com/indices/nq-100-historical-data'}},'gaps':['Stock Analysis and Yahoo volume counts differ, especially GOOGL ~13%; volume interpretations downgraded; OHLC calculations use one Yahoo series','QQQM high differs by one cent; dates and four close quotes consistent','aggregate index earnings/valuation and constituent market breadth not fully validated','latest Google10Q asset/lease bridge incomplete; no new completed DCF or approved entry orders']}
for s,k in [('^GSPC','SP500'),('^IXIC','IXIC'),('^NDX','NDX')]:assert m[s]['close']==v['indices_second_source'][k]['close']
(P/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':v['status'],'drawdown_points':points,'vol_diffs_pct':{r['symbol']:round(r['volume_difference_pct'],2) for r in closes},'normalized_end':v['normalized_last_values']},ensure_ascii=False))
