from pathlib import Path
import json
from datetime import datetime,timezone
p=Path(__file__).parent
w=p.parents[3]/'adhoc_jobs/us_market_site/worker'
rd=lambda x:json.loads(x.read_text())
def save(f,x):f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
m={x['symbol']:x for x in rd(p/'metrics.json')}
now=datetime.now(timezone.utc).isoformat()
sec='https://www.sec.gov/Archives/edgar/data/1045810/000104581026000082/nvda-20261111.htm'
def src(t,u):return {'title':t,'url':u}
def part(t,pp,ss):return dict(title=t,paragraphs=pp,sources=ss)
items=[dict(title='黄仁勋离任获确认，等待经营指引验证',fact='11月12日公开的8-K确认董事会11月11日接受黄仁勋辞去总裁、CEO及董事职务，立即生效。Colette Kress暂代CEO并继续担任CFO，Harvey Jones任董事长。NVDA常规收盘166.19美元，跌4.34%。',implication='领导层交接增加长期战略、客户关系与资本配置的不确定性。8-K未量化订单、利润或现金流损失。',judgment='继续观察。166.19美元除以最近四季GAAP稀释EPS约7.91美元为21.0倍；该EPS含投资收益。沿用昨日约9.67美元的指引年化经营EPS情景，则约17.2倍，仍高于该情景20倍估值再打八折的约155美元。该假设有待重估。',counter='长期任职的CFO接任提供执行连续性，常规收盘较日内148.80美元低点回升。不能由人事变化直接推断近期出货下降。',next='看11月17日财报对收入、毛利、客户需求、现金回收及资本承诺的更新，及董事会后续交接安排。',sources=[src('SEC 8-K',sec),src('NVDA行情对照','https://stockanalysis.com/stocks/nvda/history/'),src('Q2与Q3指引','https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2027')]),dict(title='QQQM守住200日线，三项观察档无新触发',fact='11月12日标普500跌0.35%，纳斯达克100跌0.30%，QQQM收283.39美元，距52周盘中高点回撤9.78%。',implication='SMH跌1.03%，SOXX跌0.26%，半导体基金表现分化。',judgment='继续观察常规收盘和财报兑现，暂不因单日波动改变研究条件。',counter='QQQM收盘仍高于280.80美元的200日均线，VOO回撤约3.13%，BRK.B收涨0.27%。',next='看QQQM能否持续站稳200日线及PPI、英伟达财报和联储会议纪要。',sources=[src('QQQM历史','https://stockanalysis.com/etf/qqqm/history/'),src('NYSE日历','https://www.nyse.com/trade/hours-calendars')])]
watch=[]
for s,sh in [('QQQM',314.12),('VOO',718.47),('BRK-B',596.92)]:
 x=m[s];d=-x['drawdown_pct'];watch.append(f"{s.replace('-', '.')} 常规收盘 {x['close']:.2f} 美元，Yahoo滚动高点 {x['high_52w']:.2f} 美元（{x['high_date']}），第二来源高点 {sh:.2f}。回撤 {d:.2f}%，距15%档 {15-d:.2f} 个百分点；到 {x['level_15']:.2f} 美元需再跌 {-x['additional_drop_to_15_pct'] if x['additional_drop_to_15_pct']<0 else x['additional_drop_to_15_pct']:.2f}%。25%观察价 {x['level_25']:.2f} 美元。两源收盘一致，高点差异不影响分档。")
sectors=[]
for s in 'XLK XLC XLY XLP XLV XLF XLI XLE XLU XLB XLRE SMH'.split():
 if s not in m:sectors.append(f'{s}：本地序列OHLC矛盾，11月12日指标留空。');continue
 vals=[m[s][k] for k in ('day_pct','five_session_pct','twenty_one_session_pct')]
 rel=[v-m['^GSPC'][k] for v,k in zip(vals,('day_pct','five_session_pct','twenty_one_session_pct'))]
 sectors.append(s+'：日／5日／21日 '+'／'.join(f'{v:+.2f}%' for v in vals)+'；相对标普 '+'／'.join(f'{v:+.2f}' for v in rel)+'个百分点。')
sections=[part('三项收盘观察',watch,[src(s,'https://stockanalysis.com/'+('stocks/brk.b' if s=='BRK.B' else 'etf/'+s.lower())+'/history/') for s in ['QQQM','VOO','BRK.B']]),part('行业相对表现',sectors,[src('Yahoo日线',m['SMH']['source_url'])]),part('宏观与事件',['VIX 18.70，较前次上升6.92%。本地Yahoo日线。美债日值本稿未完成核验。','下一个常规交易日为11月13日。早间采集对应美东11月12日盘后，下一盘前尚未开始。','重点核查11月13日PPI、11月17日英伟达财报、11月18日FOMC纪要。'],[src('BLS发布日历','https://www.bls.gov/schedule/2026/11_sched.htm'),src('联储日历','https://www.federalreserve.gov/newsevents/2026-november.htm'),src('英伟达交接与财报时间','https://nvidianews.nvidia.com/_gallery/download_pdf/6af5c3cc3d6332f541088655/')]),part('社区线索与覆盖限制',['FiNews读取11月12日盘后总结及新闻，页面更新时间23:18:55 UTC。以SEC 8-K核对CEO交接。','Reddit六社区New及Top日窗已请求，帖子正文、时间与评论未完成验证，本次无入选条目。'],[src('FiNews','https://finews.fyi/')])]
ext=p/'extended_quotes.json'
if ext.exists():
 e=rd(ext);pp=[]
 for a in e['observations']:
  q=a.get('post',{})
  if a['symbol'] in ['NVDA','QQQM','VOO','BRK-B','SMH'] and q.get('status')=='available':
   pp.append(f"{a['symbol']} {q['price_usd']:.2f}美元，美东 {q['bar_start_et']}，北京时间 {q['bar_start_beijing']}。")
 if pp:sections.append(part('盘后单源参考',['采集 '+e['captured_at_beijing']+'。当时盘后尚未结束，零量报价可能延续。']+pp,[src('Yahoo分钟线','https://finance.yahoo.com/quote/NVDA/')]))
prior=rd(w/'daily-brief.json')
sections+= [s for s in prior['sections'] if s['title'].startswith(('11/','FDE上市公司','AI应用专题','既有研究留存'))]
b=dict(schema_version=1,report_date='2026-11-13',market_session='2026-11-12',reviewed_at=now,summary='英伟达CEO交接已获8-K确认。QQQM回撤9.78%，三项收盘观察档无新触发。',items=items,sections=sections)
seed=rd(w/'seed.json')
a=next(a for g in seed['catalog']['groups'] for a in g['assets'] if a['symbol']=='NVDA')
a['research_status']='黄仁勋离任已确认，Colette Kress暂代CEO；等待财报复核经营影响'
a['facts']['governance_event'].update(latest_event_date='2026-11-11',reviewed_date='2026-11-13',reviewed_at=now,latest_confirmed='11/12公开8-K确认11/11董事会接受黄仁勋辞职，Kress暂代CEO并留任CFO，Jones任董事长。',board_position='董事会已启动正式CEO搜索；独立调查结论仍待披露。',financial_impact='交接8-K未量化经营影响。')
a['facts']['fact_lines'].append(items[0]['fact'].split('NVDA常规')[0])
a['facts']['sources'].append(src('11/12公开的CEO交接8-K',sec))
save(w/'daily-brief.json',b);save(w/'seed.json',seed);save(p/'daily_brief_candidate.json',b)
save(p/'reddit_sources.json',dict(full_scan_complete=False,selected_items=[],coverage='12个列表页已请求，未完成正文及绝对时间验证'))
(p/'reddit_digest.md').write_text('六社区New/Top日窗已请求，未完成原帖日期和评论验证。无入选条目。\n')
