from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import json
P=Path(__file__).resolve().parent
M={r['symbol']:r for r in json.loads((P/'metrics.json').read_text())}; E=json.loads((P/'extended_quotes.json').read_text()); eq={r['symbol']:r for r in E['observations']}
# Values read from dated Stock Analysis regular-session rows and extended headers through the web tool.
S={'QQQ':(715.34,703.99,'19:26',37975249),'QQQM':(294.53,289.56,'19:16',2510918),'VOO':(707.32,702.51,'19:20',5122767),'BRK-B':(541.96,545.49,'19:06',4068361),'GOOGL':(283.82,280.28,'19:26',139691848),'SOFI':(17.61,17.05,'19:26',65133427),'RRX':(163.62,160.95,'18:38',None),'CGNX':(58.97,57.18,'18:54',None),'ATS':(19.09,19.09,'19:00',167524),'NVDA':(213.66,209.48,'19:31',77304159),'SMH':(561.67,541.03,'19:21',5966137),'SGOV':(100.71,100.71,'19:15',21018887)}
regular=[]; cross=[]; et=ZoneInfo('America/New_York');bj=ZoneInfo('Asia/Shanghai')
for s,(close,post,hhmm,vol) in S.items():
 slug='brk.b' if s=='BRK-B' else s.lower(); typ='etf' if s in ['QQQ','QQQM','VOO','SMH','SGOV'] else 'stocks';url=f'https://stockanalysis.com/{typ}/{slug}/history/'
 row={'symbol':s,'session':'2026-10-29','provider_close_usd':M[s]['close'],'second_source_close_usd':close,'source_url':url,'source_scope':'regular dated row and dated extended-price header','close_match':abs(M[s]['close']-close)<.005}
 if vol: row.update(second_source_volume=vol,provider_volume=M[s]['volume'],provider_volume_difference_pct=(M[s]['volume']/vol-1)*100)
 regular.append(row)
 stamp=datetime.fromisoformat('2026-10-29T'+hhmm+':00').replace(tzinfo=et);q=eq[s]['post'];assert q['session']=='2026-10-29'
 cross.append({'symbol':s,'regular_close_usd':close,'yahoo_price_usd':q['price_usd'],'yahoo_time_et':q['bar_start_et'],'yahoo_time_beijing':q['bar_start_beijing'],'yahoo_minute_volume':q['minute_volume'],'source_url':url,'second_source_price_usd':post,'second_source_time_et':stamp.isoformat(),'second_source_time_beijing':stamp.astimezone(bj).isoformat(),'second_source_change_vs_same_regular_pct':(post/close-1)*100,'price_difference_yahoo_minus_second_usd':round(q['price_usd']-post,4),'comparison_status':'different_time_snapshots_not_same_tick','display_policy':'latest Yahoo minute reference; all current observations have zero volume, not proof of a new trade; second source shown separately'})
assert all(r['close_match'] for r in regular)
verification={'report_date_beijing':'2026-10-30','quote_session_us':'2026-10-29','checked_at_utc':datetime.now(timezone.utc).isoformat(),'regular_closes':regular,'after_hours_cross_checks':cross,'watch_high_checks':{'QQQ':{'yahoo':762.86,'stock_analysis':762.86,'date':'2026-10-06'},'QQQM':{'yahoo':314.11,'stock_analysis':314.12,'date':'2026-10-06','difference_disclosed':True},'VOO':{'yahoo':718.47,'stock_analysis':718.47,'date':'2026-10-06'},'BRK-B':{'yahoo':549.96,'stock_analysis':549.96,'date':'2026-10-22'}},'source_type':'third_party_cross_check; not official consolidated price feed'}
(P/'quote_verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
# No cross-source price is silently substituted into the display. The renderer uses raw captured minute references.
(P/'extended_verification.json').write_text(json.dumps({'quote_session_us':'2026-10-29','rows':[],'cross_checks':cross,'method':'No price overrides; snapshots at different times do not establish same-tick agreement','captured_at_beijing':E['captured_at_beijing'],'latest_capture_post_window_ended':False},ensure_ascii=False,indent=2)+'\n')
lines=['# 盘前盘后来源与时段详情｜2026-10-30','','常规基线是美东10/29收盘。采集北京时间'+E['captured_at_beijing']+'；10/29盘后仍在交易，本次不是最终盘后收盘。下一常规交易日10/30，盘前当时尚未开始。以下Yahoo均为零成交量的分钟参考，不能据此认定有新成交或可成交；Stock Analysis各自较早时点，不伪称同一笔报价。','','| 标的 | Yahoo参考价／北京时刻 | Stock Analysis价／北京时刻 | 差值（美元） |','|---|---|---|---:|']
for r in cross:
 lines.append(f"| {r['symbol']} | {r['yahoo_price_usd']:.2f} / {datetime.fromisoformat(r['yahoo_time_beijing']):%m/%d %H:%M:%S} | [{r['second_source_price_usd']:.2f}]({r['source_url']}) / {datetime.fromisoformat(r['second_source_time_beijing']):%m/%d %H:%M} | {r['price_difference_yahoo_minus_second_usd']:+.2f} |")
lines+=['','盘后涨跌均相对各自同日常规收盘，盘前相对前一个常规收盘，不相加。本次历史盘前数据仅存于原始JSON，不展示成10/30盘前。无20:00–04:00夜盘数据。时段元数据及双时区见[原始快照](./extended_quotes.json)和[跨源记录](./extended_verification.json)。']
(P/'extended_detail.md').write_text('\n'.join(lines)+'\n')
print('Cross-checked',len(regular),'regular closes; extended snapshots preserved with differences.')
