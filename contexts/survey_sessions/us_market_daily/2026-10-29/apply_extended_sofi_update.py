from pathlib import Path
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
import json,hashlib
P=Path(__file__).resolve().parent
report=P/'report.md'
if not (P/'report_before_extended_update.md').exists():(P/'report_before_extended_update.md').write_bytes(report.read_bytes())
s=(P/'report_before_extended_update.md').read_text()
m={r['symbol']:r for r in json.loads((P/'metrics.json').read_text())}
ext=json.loads((P/'extended_quotes.json').read_text())
# Second source explicitly labels these observations After-hours, including their date and ET minute.
secondary={'GOOGL':(292.50,'19:59'),'SOFI':(16.87,'19:59'),'QQQ':(718.05,'19:59'),'QQQM':(295.85,'19:59'),'VOO':(706.95,'19:55'),'BRK-B':(543.09,'19:58')}
verification={'captured_primary_at_utc':ext['captured_at_utc'],'secondary_read_at_utc':'2026-10-29T02:12:20Z','quote_session_us':'2026-10-28','display_source':'Stock Analysis explicitly dated after-hours snapshot','secondary_cross_check':'Yahoo positive minute-bar close; zero volumes are indicative, not evidence of a new trade','notes':['Sources use different venues/timestamps, slight differences disclosed; not guaranteed executable prices','No change to original regular OHLC, 60-day charts or four-symbol alert stage','Next regular session2026-10-29 verified inNYSEcalendar; premarket not started at capture'],'rows':[]}
rows=[];prerows=[]
for symbol in ['GOOGL','SOFI','QQQ','QQQM','VOO','BRK-B']:
 r=next(i for i in ext['observations'] if i['symbol']==symbol);price,ettime=secondary[symbol];baseline=m[symbol]['close'];change=(price/baseline-1)*100
 path='stocks/'+('brk.b' if symbol=='BRK-B' else symbol.lower()) if symbol in ['GOOGL','SOFI','BRK-B'] else 'etf/'+symbol.lower()
 url='https://stockanalysis.com/'+path+'/'
 label='BRK.B' if symbol=='BRK-B' else symbol
 bjtime=datetime.fromisoformat('2026-10-28T'+ettime+':00-04:00').astimezone(ZoneInfo('Asia/Shanghai')).strftime('%H:%M')
 rows.append(f'| [{label}]({url}) | {baseline:.2f} | {price:.2f} | {change:+.2f}% | 10/28 {ettime} EDT / 10/29 {bjtime} 北京 |')
 post=r['post'];yp=post.get('price_usd');diff=None if yp is None else (yp/price-1)*100
 verification['rows'].append({'symbol':symbol,'regular_close_usd':baseline,'afterhours_display_usd':price,'afterhours_change_vs_same_regular_pct':change,'display_quote_time_et':f'2026-10-28T{ettime}:00-04:00','display_quote_time_beijing':f'2026-10-29T{bjtime}:00+08:00','source_url':url,'yahoo_snapshot':post,'yahoo_vs_display_pct':diff,'difference_explained':'Provider/venue and timestamps differ; no mixing or threshold update'})
 pre=r['pre']
 if pre['status']=='available':
  ts=datetime.fromisoformat(pre['bar_start_et']);bj=datetime.fromisoformat(pre['bar_start_beijing'])
  prerows.append(f"| {label} | {pre['price_usd']:.2f} | {pre['change_vs_reference_pct']:+.2f}% | {pre['reference_session']} / {pre['reference_close_usd']:.2f} | {ts:%m/%d %H:%M} EDT / {bj:%m/%d %H:%M} 北京 |")
 else:prerows.append(f'| {label} | 缺失 | 缺失 | 缺失 | {pre["status"]} |')
assert verification['rows'][0]['afterhours_display_usd']==292.5
(P/'extended_verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
pretable='| 标的 | 历史盘前美元 | 相对前次常规收盘 | 分母日期/美元 | 报价时间 |\n| --- | ---: | ---: | --- | --- |\n'+'\n'.join(prerows)
detail='''# 盘前盘后读取范围与历史盘前｜2026-10-29

本次采集为北京时间10/29 10:12–10:15左右；美东仍是10/28晚间。10/29的标准盘前04:00EDT（北京16:00）尚未开始，不能拿10/28盘前报价填成今日盘前。下面只是上一交易日历史盘前，不能反映Google盘后新财报。

'''+pretable+'''

历史盘前来自Yahoo分钟数据，未取得独立同一分钟第二来源，且盘前/盘后末段成交量被提供方填0。价格只是来源记录中的参考/延续报价，不能据其证明最新实际成交量、价差或流动性。

主报告盘后展示使用Stock Analysis明确标注After-hours的时点，Yahoo分钟价格交叉比较。GOOGL同为292.50；QQQ、QQQM、SOFI差0.01–0.05美元，VOO差0.18、BRK.B差0.09，报价时刻和场所不同，不伪称同笔成交一致。观察档仍按原常规收盘，不因场外快照改alert_state。

[分钟原始快照与计算](./extended_quotes.json) · [逐标的来源与差异](./extended_verification.json)
'''
(P/'extended_detail.md').write_text(detail)
section='''**盘前与盘后观察**

**Google盘后292.50美元，较324.89常规收盘−9.97%。** 这是美东10/28 19:59、北京10/29 07:59的来源快照，反映了财报后的重新定价；它既不是10/29常规收盘，也不保证下一次开盘幅度。[盘后报价](https://stockanalysis.com/stocks/googl/)

本次取数在北京时间 **10/29 10:12–10:15**。美东10/28标准盘后已结束；**10/29盘前尚未开始，预计北京时间16:00开始**（正常交易日04:00 EDT）。表中盘后涨跌统一相对10/28同日常规收盘；盘前涨跌应相对前一次常规收盘，百分比不能相加。

| 标的 | 10/28常规收盘（美元） | 10/28盘后参考价（美元） | 盘后相对收盘 | 来源报价时间（美东 / 北京） |
| --- | ---: | ---: | ---: | --- |
'''+ '\n'.join(rows)+'''

展示价采用各行Stock Analysis链接的明确盘后时点，Yahoo分钟数据另核；Google同为292.50，其余存在0.01–0.18美元差异，已逐项保留。Yahoo末段成交量为0，可能是延续报价，不能当新成交或保证可成交价。10/29盘前本次没有新报价；[上一交易日历史盘前、来源差异与口径](./extended_detail.md)放在详情。两张常规曲线与四标的收盘提醒继续使用原统一序列。

'''
s=s.replace('⚠️ Google、微软财报均在上述收盘后公布，今天的收盘表尚未完整反映新财报。本日报将经营事件单列，盘后快照不混入曲线、阈值或常规收盘涨跌。','⚠️ Google、微软财报已在上述收盘后公布。**本更新版已加入财报后的盘后反应、明确盘前状态，并新增SOFI固定研究观察**；常规收盘曲线与盘前盘后分别呈现。')
s=s.replace('1. **Google：经营增长成立，现金回报仍需等待，昨天的入场档暂停沿用。**','1. **Google三季报已经发布，盘后下跌约10%，旧入场档继续暂停沿用。** SEC受理8-K为北京时间10/29 04:01:33；最新盘后快照292.50，相对常规收盘−9.97%。')
oldthird='3. **机器人供应链：RRX的便宜程度高度依赖盈利调整。** 161.09的收盘只比昨日主观165.07基准低2.41%。恢复部分收购摊销成本后，参考价值会明显降低，现价缺少充分安全边际；11/3季报重点看现金转化与负债。最强反证是收购摊销高于实际经济损耗、增长和去杠杆继续兑现。今天没有新增已低估股票。[RRX价格](https://stockanalysis.com/stocks/rrx/history/) · [公司调整表](https://investors.regalrexnord.com/investors/ir-news/press-release-details/2026/REGAL-REXNORD-REPORTS-SECOND-QUARTER-2026-FINANCIAL-RESULTS/default.aspx) · [本次压力检查](./robotics_update.md)'
newthird='3. **SOFI加入固定观察，先查信贷质量，状态为估值待完成。** 10/27已公布Q3，GAAP净收入同比+44%、稀释EPS0.18；但个人贷核销受逾期贷款出售影响，不能只看表面2.26%。17.14收盘对应管理层2027调整EPS展望约19倍，尚不足证明低估。对你控制回撤的目标，它需要独立的信用与资本压力情景。[公司财报](https://investors.sofi.com/news/news-details/2026/SoFi-Reports-Third-Quarter-2026-with-Record-Net-Revenue-of-1-4-Billion-Net-Income-of-241-Million-and-Raises-Full-Year-Guidance/default.aspx) · [SOFI研究卡](./sofi_research.md)'
assert oldthird in s;s=s.replace(oldthird,newthird)
s=s.replace('**Google估值结果**',section+'**Google估值结果**',1)
s=s.replace('完整Q3证券分拆、租赁和索偿仍待核验，因此旧180–195及后续档暂停机械沿用；今天不发布新的精确买入区间。','本次已直接检查SEC官方近期申报：最近10-Q仍是7/23、对应6/30。**缺的是完整Q3证券分拆、租赁和索偿明细，财报结果本身已公布**；旧180–195及后续档继续暂停机械沿用，今天不发布新的精确买入区间。[Google新增官方复核](./google_update/google_latest_followup.md)')
sofi=m['SOFI']
sofi_section=f'''**SOFI研究观察**

SOFI（SoFi Technologies）已列为独立固定研究对象，**尚未确认持仓，估值待完成**。它是数字银行与金融平台，研究重点区别于机器人供应链；原四标的15%/25%提醒范围不变。

最新2026Q3于10/27已公布：GAAP净收入13.851亿美元、同比+44%，净利润2.410亿美元、稀释EPS0.18，存款513亿美元。正面是获客、交叉销售和存款融资优势；主要反证是信用周期和贷款估值。个人贷账面年化核销2.26%受逾期贷款销售影响，公司估算剔除该影响、含回收约3.4%；公允价值模型的违约假设由4.77%升至5.10%，**模型假设与已实现违约不是同一指标**。[SoFi官方财报](https://investors.sofi.com/news/news-details/2026/SoFi-Reports-Third-Quarter-2026-with-Record-Net-Revenue-of-1-4-Billion-Net-Income-of-241-Million-and-Raises-Full-Year-Guidance/default.aspx)

以17.14常规收盘计算，管理层2027调整EPS展望0.90对应约19.04倍，9月底有形净资产7.48对应约2.29倍P/TBV。前者是未来调整口径，不是TTM或已兑现GAAP盈利；银行存款属于经营资金，不能直接照搬Google/工业公司的净现金DCF。当前先研究，暂不因上涨追入；下一步补Q3完整10-Q、监管资本、贷款出售后保留风险及正常化每股收益情景。[SOFI事实、反证与分母](./sofi_research.md)

| 标的 | 10/28收盘 | 当日 | 近5交易日 | 近21交易日 | 52周盘中高点/日期 | 距高点回撤 | 50/200日均线 |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| SOFI | {sofi['close']:.2f} | {sofi['day_pct']:+.2f}% | {sofi['five_session_pct']:+.2f}% | {sofi['twenty_one_session_pct']:+.2f}% | {sofi['high_52w']:.2f} / {sofi['high_date']} | {-sofi['drawdown_pct']:.2f}% | {sofi['ma50']:.2f} / {sofi['ma200']:.2f} |

该行全部美元、常规收盘口径；回撤47.63%也不能自动推出便宜或套用原ETF加仓规则。盘后16.87及时间见前表，常规收盘与Yahoo/Stock Analysis一致，盘后两源差一美分。[SOFI研究来源](./sofi_sources.json) · [盘后核验](./extended_verification.json)

'''
s=s.replace('**主观察表**',sofi_section+'**主观察表**',1)
s=s.replace('本次所读公司','本次所读公司')
s=s.replace('HTML沿用模板，未公开托管，不操作账户或自动交易。','HTML增加盘前盘后与SOFI导航，需定向检查桌面/手机排版和导航交互；未公开托管，不操作账户或自动交易。')
s += '\n[盘前盘后快照](./extended_quotes.json) · [盘前盘后交叉核验](./extended_verification.json) · [本次新增需求核验](./user_update_verification.json)\n'
report.write_text(s)
# Keep current source generator from silently overwriting this interactive update.
(P/'interactive_update_manifest.json').write_text(json.dumps({'updated_at_utc':datetime.now(timezone.utc).isoformat(),'reason':'User requested released Google earnings, pre/post quotes, and SOFI fixed research','source_before':'report_before_extended_update.md','script':'apply_extended_sofi_update.py','baseline_generator_warning':'build_report.py creates morning baseline only; reapply this script to retain this update','alert_contract_changed':False},ensure_ascii=False,indent=2)+'\n')
print('updated reviewed Markdown; preserved morning baseline')
