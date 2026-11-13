from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import json, ast, csv

OUT = Path(__file__).parent
ET, BJ = ZoneInfo('America/New_York'), ZoneInfo('Asia/Shanghai')
now = datetime.now(timezone.utc)
tree = ast.parse((OUT/'macro_collect.py').read_text())
urls = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SOURCES' for t in n.targets))
urls['glob_calendar'] = 'https://investors.globant.com/2026-11-05-Globant-to-Announce-Third-Quarter-2026-Financial-Results-on-November-19th'
def source(key, title): return {'title': title, 'url': urls[key]}
def event(name, date, time, keys, note='', period=None, in_window=True):
    dt = datetime.fromisoformat(date + 'T' + time).replace(tzinfo=ET) if time else None
    return {'name': name, 'date_et': date, 'time_et': time, 'timezone': 'America/New_York', 'datetime_et': dt.isoformat() if dt else None, 'datetime_bjt': dt.astimezone(BJ).isoformat() if dt else None, 'reference_period': period, 'status': 'scheduled_not_released', 'within_next_seven_us_calendar_days': in_window, 'note': note, 'source_urls': [urls[k] for k in keys]}
events = [
 event('美国初请失业金', '2026-11-12', '08:30:00', ['dol_claims_schedule'], '按 DOL 周四 08:30 EST 规则；11/12 非例外。2026 年 11 月的例外是 11/25，非本次。'),
 event('Moderna Analyst Day', '2026-11-12', None, ['mrna_sec_calendar','mrna_events'], 'SEC 确认日期；当前可打开 IR 正文未返回具体时刻，09:00 EST 仅见搜索索引，故时间留空。不是季度财报。'),
 event('Cisco FY2027 Q1 业绩电话会', '2026-11-12', '16:30:00', ['csco_calendar'], '公告另明确当日常规收盘后发布业绩，未明示发布分钟；16:30 为电话会时间。', '截至 2026-10-24 的财季'),
 event('Applied Materials FY2026 Q4/全年业绩电话会', '2026-11-12', '16:30:00', ['amat_calendar'], '官方公告核实电话会时刻；业绩稿具体发布分钟未说明，不把电话会时刻冒充发布时间。', 'FY2026 Q4/全年'),
 event('美国 PPI', '2026-11-13', '08:30:00', ['bls_schedule_nov'], period='2026-10'),
 event('美国进出口物价指数', '2026-11-17', '08:30:00', ['bls_schedule_nov'], period='2026-10'),
 event('美国工业产出与产能利用率', '2026-11-17', '09:15:00', ['fed_nov_calendar'], period='2026-10'),
 event('NVIDIA FY2027 Q3 业绩发布', '2026-11-17', '16:20:00', ['nvda_calendar'], '公司用 approximately，属于预计发布时间；原公告 13:20 PT。', '截至 2026-10-25 的财季'),
 event('NVIDIA FY2027 Q3 业绩电话会', '2026-11-17', '17:00:00', ['nvda_calendar'], '原公告 14:00 PT / 17:00 ET。', '截至 2026-10-25 的财季'),
 event('FOMC 10/27–28 会议纪要', '2026-11-18', '14:00:00', ['fed_nov_calendar'], '会议纪要，不是新的利率决议。', '2026-10-27/28'),
 event('Globant Q3 业绩电话会（窗口外前瞻）', '2026-11-19', '16:30:00', ['glob_calendar'], '11/19 超出本次 11/12–18 日窗口；业绩当日常规收盘后发布，具体分钟未说明。', '截至 2026-09-30 的季度', False),
 event('美国非农就业报告', '2026-12-04', '08:30:00', ['bls_jobs_schedule'], '不在未来 7 日内。', '2026-11', False),
 event('下一次 FOMC 会议开始', '2026-12-08', None, ['fomc_calendar'], '会议 12/8–9；本次不杜撰具体决议发布时间。不在未来 7 日内。', in_window=False),
 event('美国 CPI', '2026-12-10', '08:30:00', ['bls_cpi_schedule'], '10 月 CPI 已于 11/10 发布，下一期是 12/10；本次 7 日窗口没有新的 CPI。', '2026-11', False),
]
receipts = json.loads((OUT/'macro_raw/http_receipts.json').read_text())
vix_csv = list(csv.DictReader((OUT/'macro_raw/cboe_vix_history.csv').open()))[-1]
data = {
 'schema_version': 1, 'report_date': '2026-11-12', 'market_session': '2026-11-11', 'reviewed_at': now.isoformat(), 'reviewed_at_bjt': now.astimezone(BJ).isoformat(),
 'calendar': {'previous_completed_session': '2026-11-11', 'next_session': '2026-11-12', 'equity_status': '11/11 老兵日 NYSE 正常开市，下一交易日 11/12；不属于周末休市简版。', 'regular_close_et': '2026-11-11T16:00:00-05:00', 'regular_close_bjt': '2026-11-12T05:00:00+08:00', 'after_hours_ends_et': '2026-11-11T20:00:00-05:00', 'after_hours_ends_bjt': '2026-11-12T09:00:00+08:00', 'after_hours_status_at_review': 'ongoing', 'next_premarket_start_et': '2026-11-12T04:00:00-05:00', 'next_premarket_start_bjt': '2026-11-12T17:00:00+08:00', 'next_premarket_status': 'not_started', 'next_regular_open_et': '2026-11-12T09:30:00-05:00', 'next_regular_open_bjt': '2026-11-12T22:30:00+08:00', 'bond_market_note': 'SIFMA 建议美国美元计价固定收益现货市场 11/11 全天休市；不是对股票或所有期货产品的休市判断。Fed 日历也将 11/11 统计发布顺延 11/12。', 'source_urls':[urls[k] for k in ['nyse_calendar','sifma_calendar','fed_nov_calendar']]},
 'vix': {'session': '2026-11-11', 'value':17.49, 'previous_close':19.46, 'change_points':round(17.49-19.46,2), 'change_pct':(17.49/19.46-1)*100, 'unit':'index_points', 'kind':'cash_index_close', 'cboe_display_asof':'9:15 PM 11/11/2026 (页面未注明时区)', 'second_source_display_asof':'3:15 PM CST 11/11/26', 'second_source_datetime_et':'2026-11-11T16:15:00-05:00', 'second_source_datetime_bjt':'2026-11-12T05:15:00+08:00', 'verification':'Cboe 官方现值与 WSJ 明确日期的 OHLC CLOSE 一致。Cboe 官方下载 CSV 尚只到 11/10，未把该 CSV 冒充 11/11 收盘证据。', 'cboe_csv_latest':vix_csv, 'source_urls':[urls[k] for k in ['cboe_vix','wsj_vix','cboe_vix_history']]},
 'treasury': {'observation_date':'2026-11-10', 'requested_equity_session':'2026-11-11', 'new_row_for_requested_session':False, 'two_year_pct':4.73, 'ten_year_pct':4.98, 'spread_10y_minus_2y_bp':25.0, 'daily_change_for_2026_11_11_bp':None, 'basis':'美国财政部 Daily Treasury Par Yield Curve/CMT；约 15:30 ET 指示性买方报价，不是实时成交。', 'note':'11/11 老兵日债券市场休市，官方页面最新有效行仍为 11/10；不生成 11/11 的新收益率或零变动。', 'source_url':urls['treasury']},
 'sgov': {'sec_30_day_yield_pct':3.85, 'asof':'2026-11-10', 'previous_verified_yield_pct':3.85, 'previous_verified_asof':'2026-11-09', 'yield_value_changed':False, 'disclosure_date_advanced':True, 'trailing_12m_yield_pct':3.63, 'expense_ratio_pct':0.09, 'note':'本次新访问官方页，SEC 收益率数值无变化，只推进官方披露日；不把 trailing yield 当 SEC 收益率，不把任一收益率当未来总回报。', 'source_url':urls['sgov']},
 'event_window_et':['2026-11-12','2026-11-18'], 'events':events,
 'interpretation': {'judgment':'VIX 下降说明本次期权隐含波动降温，但债券市场没有 11/11 新官方收益率可供交叉确认，不能据此认定折现率压力解除或估值已便宜。', 'strongest_counterpoint':'VIX 不是盈利或估值指标；债市休市造成信号不同步，11/12 重开与 11/13 PPI 可能改变判断。', 'next_check':'11/12 美债重开、今晚北京时间 21:30 初请失业金、11/13 21:30 PPI，以及 CSCO/AMAT 财报的订单、利润率和现金流。'},
 'gaps':['MRNA 11/12 Analyst Day 日期已由 SEC 核实；当前可打开 IR 原文没有具体小时，不能将搜索摘要 09:00 EST 升格为已核时刻。','Cboe 现值页面没有明确时间区域；采用 WSJ CST 时刻作交叉说明。官方 CSV 当次下载仍止于 11/10。','BLS、AMAT 和 MRNA SEC 本机 HTTP 为 403；web 工具可访问正文的结果已留档。NYSE 本机 DNS 超时，WSJ 本机 TLS 失败；web 工具读取成功。','日历精选与观察名单相关事件，并非覆盖所有公司的完整财报库；未来日程可能由发布方调整。'],
 'sources': [{'id':k,'url':u,'access':'fresh_current_task','http_receipt':next((r for r in receipts if r['id']==k),None)} for k,u in urls.items()]
}
sections = [
 {'title':'宏观：波动降温，但老兵日没有新的官方美债收益率', 'paragraphs':[
 '11/11 VIX 收盘 17.49 点，较前收 19.46 下降 10.12%（−1.97 点）；Cboe 现值与 WSJ 当日收盘一致。VIX 的单位是指数点，不是美元。',
 '11/11 老兵日美股正常交易，美元固定收益现货市场按 SIFMA 建议休市。美国财政部最新可读收益率仍截至 11/10：2 年 4.73%、10 年 4.98%，10–2 年利差 +25 基点；这不是 11/11 的新收盘，也不写作当日零变动。',
 '研究判断：期权隐含波动降温，有利于短期风险情绪；反证是它不能证明盈利兑现或估值便宜，债市信号也不同步。下一步看 11/12 美债重开、初请失业金和 11/13 PPI。'
 ], 'sources':[source('cboe_vix','Cboe VIX'),source('wsj_vix','WSJ VIX 历史收盘与 CST 时刻'),source('treasury','美国财政部 2026 年 11 月收益率'),source('sifma_calendar','SIFMA 2026 债市休市建议')]},
 {'title':'未来一周：今晚初请、周五 PPI，11/18 公布 FOMC 纪要', 'paragraphs':[
 '下一美股常规交易日为 11/12，开盘 09:30 EST＝北京时间今晚 22:30；盘前 04:00 EST＝17:00，当前尚未开始。北京时间本次早间 07:30 对应 11/11 18:30 EST，11/11 盘后尚未结束。',
 '11/12 08:30 EST＝北京时间今晚 21:30：初请失业金。11/13 08:30 EST＝21:30：10 月 PPI。11/17 08:30 EST＝21:30：10 月进出口物价；同日 09:15 EST＝22:15：工业产出。',
 '11/18 14:00 EST＝北京时间 11/19 03:00：10/27–28 的 FOMC 会议纪要，不是新的利率决议。下一次 FOMC 会议为 12/8–9；下一次非农 12/4 08:30 EST、CPI 12/10 08:30 EST，均不在本次 7 日窗口。10 月 CPI 已于 11/10 发布，不再列作待公布。',
 '公司事件：CSCO 与 AMAT 11/12 的业绩电话会均为 16:30 EST＝北京时间 11/13 05:30；CSCO 明确当日收盘后发业绩，AMAT 公告未明示发布分钟。NVDA 预计 11/17 16:20 EST＝北京时间 11/18 05:20 发业绩，17:00 EST＝06:00 开电话会。MRNA 11/12 Analyst Day 日期已核，具体时刻仍留缺口，不当作季度财报。'
 ], 'sources':[source('nyse_calendar','NYSE 交易时间与日历'),source('dol_claims_schedule','DOL 初请发布规则'),source('bls_schedule_nov','BLS 11 月日历（ET）'),source('fed_nov_calendar','Federal Reserve 11 月日历'),source('fomc_calendar','FOMC 会议日期'),source('bls_cpi_schedule','BLS CPI 日程'),source('bls_jobs_schedule','BLS 就业报告日程'),source('csco_calendar','Cisco 官方财报公告'),source('amat_calendar','AMAT 官方电话会公告'),source('nvda_calendar','NVIDIA 官方财报公告'),source('mrna_sec_calendar','Moderna SEC 季报新闻稿中的 Analyst Day 日期')]},
 {'title':'SGOV 与来源限制', 'paragraphs':[
 'iShares 本次新读取的 30 日 SEC 收益率仍为 3.85%，官方截至日期为 11/10（上次为 11/9）。仅披露日推进，没有收益率数值变化；3.63% 是另一个 12 个月 trailing yield 口径，两者都不是未来总回报承诺。',
 'Cboe 官方 CSV 当次下载只到 11/10，11/11 收盘以官方现值与 WSJ 当日历史行核验；Cboe 页面时间未写时区，WSJ 明示 15:15 CST。MRNA 活动具体小时只在搜索索引出现，打开原文未取得，因此未填确定时刻。'
 ], 'sources':[source('sgov','iShares SGOV 官方披露'),source('cboe_vix_history','Cboe 官方历史 CSV'),source('mrna_events','Moderna 官方活动页')]}
]
(OUT/'macro_calendar.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
(OUT/'macro_public_sections.json').write_text(json.dumps(sections,ensure_ascii=False,indent=2)+'\n')
md = '# 宏观与事件核验｜北京时间 2026-11-12\n\n'
md += '实际复核 UTC：'+now.isoformat()+'；北京时间：'+now.astimezone(BJ).isoformat()+'。本次重新访问来源，旧数据仅在明确标注原观测日时保留。\n\n'
for s in sections:
    md += '## '+s['title']+'\n\n'+'\n\n'.join(s['paragraphs'])+'\n\n来源：'+'；'.join('['+x['title']+']('+x['url']+')' for x in s['sources'])+'\n\n'
md += '## 结构化事件表（America/New_York）\n\n|事件|美国东部日期/时间|北京时间|口径|\n|---|---|---|---|\n'
for e in events:
    md += '|'+e['name']+'|'+(e['datetime_et'] or e['date_et']+' 时刻未核')+'|'+(e['datetime_bjt'] or '时刻未核')+'|'+e['note']+'|\n'
md += '\n## 获取缺口\n\n'+'\n'.join('- '+s for s in data['gaps'])+'\n\n原始 HTTP/CSV 与逐项采集时刻见 `macro_raw/http_receipts.json`；web 工具当前读取正文见同目录 `webtool_fresh_reads.json` 与 `webtool_calendar_supplement.json`。不以 HTTP 报错页冒充原文，不用搜索摘要填确定时刻。\n'
(OUT/'macro_calendar.md').write_text(md)
print(json.dumps({'reviewed_at':now.isoformat(),'vix':data['vix']['value'],'vix_change_pct':data['vix']['change_pct'],'treasury_date':data['treasury']['observation_date'],'sgov':data['sgov'],'events':len(events),'public_sections':len(sections)},ensure_ascii=False))
