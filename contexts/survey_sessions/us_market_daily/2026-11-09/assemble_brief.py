"""Publish only the newly verified public governance fact; preserve market dates."""
from pathlib import Path
from datetime import datetime, timezone
import copy
import json

HERE = Path(__file__).resolve().parent
SITE = HERE.parents[3] / 'adhoc_jobs/us_market_site'
def read(path):
    return json.loads(path.read_text())
def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

prior_path = HERE / 'daily_brief_before.json'
if not prior_path.exists():
    prior_path.write_bytes((SITE / 'worker/daily-brief.json').read_bytes())
prior = read(prior_path)
company = read(HERE / 'public_company_sections.json')
company = json.loads(json.dumps(company, ensure_ascii=False).replace('由独立董事委员会及外部独立法律顾问监督调查', '由独立董事委员会监督调查、外部独立法律顾问协助').replace('由独立董事委员会和外部独立法律顾问监督', '由独立董事委员会监督、外部独立法律顾问协助').replace('独立董事委员会及外部独立法律顾问监督调查', '独立董事委员会监督调查，外部独立法律顾问协助'))
social = read(HERE / 'public_source_sections.json')
calendar = read(HERE / 'calendar_yield_check.json')
now = datetime.now(timezone.utc).isoformat()
retained = []
for old in prior['sections']:
    if old['title'].startswith(('休市', 'Reddit', 'FiNews')):
        continue
    section = copy.deepcopy(old)
    if section['title'].startswith('BRK.B｜'):
        section['title'] = '11/8研究留存｜' + section['title']
        section['paragraphs'].insert(0, '以下是11/8已核的11/7财报研究，本次保留原日期，未把旧披露重新当作今日新增。')
    section['paragraphs'] = [p.replace('今天无新增核验结论。', '本次未重做该模型。').replace('不代表11/8已重估', '不因后续行情刷新而代表已重估') for p in section['paragraphs']]
    if section['title'].startswith('11/5估值专题留存'):
        section['paragraphs'] = [p.replace('同日常规收盘 →', '11/4常规收盘 →').replace('当前四家', '按11/4参考价，四家').replace('当前需更高', '按11/4参考价需更高').replace('现价', '11/4参考价').replace('当前227.11', '11/4的227.11').replace('当前85.81', '11/4的85.81').replace('目前估值', '当时估值').replace('财报后约51美元', '财报后当时约51美元的价格参照') for p in section['paragraphs']]
        section['paragraphs'] = ['11/6补充核验留存：完整Q3 10-Q已于11/5取得，电话会已发生但原音未听。现金留任上限与交割条件以所附11/5完整10-Q为核查入口；上述条件模型尚未完成交割后的独立重估，不把旧假设当最新估值。' if p.startswith('11/6更新：完整Q3 10-Q') else p for p in section['paragraphs']]
    retained.append(section)

session = {
    'title': '休市简报｜最近11/6收盘，11/9北京22:30恢复常规交易',
    'paragraphs': [
        '北京11/9早晨对应美东11/8周日，最近已完成常规交易日仍为11/6；下一次常规开盘为美东11/9 09:30 EST／北京时间22:30。11/9盘前尚未开始，11/6盘后已结束；不含券商夜盘。',
        '没有新收盘，三项15%／25%收盘观察状态不变，未产生新触发；本次不重复完整旧行情和60日图。历史继续按已完成美国常规交易日一条，新研究更新11/6同一条，不新增周末行情日档。',
    ],
    'sources': [{'title': 'NYSE交易时间与2026休市日历', 'url': 'https://www.nyse.com/trade/hours-calendars'}],
}
source_map = {s['id']: s for s in calendar['sources']}
cal = {
    'title': '本周已排事件与SGOV复核｜时间未变',
    'paragraphs': [
        '11/10 CPI、11/12初请、11/13 PPI均为08:30 EST／北京时间21:30；本周无预定FOMC会议或月度非农发布。日程已重新读取，未发现改期。',
        'Cisco与AMAT业绩电话会均为11/12 16:30 EST／北京时间11/13 05:30，电话会时间不等于公告精确时刻。Moderna 11/12分析师日日期由SEC确认；09:00 EST仅有官方搜索索引支持，直接动态事件内容未取得，具体时刻仍留核验缺口。',
        'SGOV官方30日SEC收益率仍为3.83%，数据截至11/5，与11/7记录相同；这是标准化收益率，不是未来回报保证、12个月派息率或总回报。没有把报价日期用作收益率日期。',
    ],
    'sources': [{'title': label, 'url': source_map[key]['url']} for key, label in [
        ('cpi', 'BLS CPI日程'), ('bls_nov', 'BLS 11月日程'), ('claims', 'DOL初请发布时间'),
        ('fomc', '美联储会议日程'), ('jobs', 'BLS就业报告日程'), ('csco', 'Cisco电话会公告'),
        ('amat', 'AMAT电话会公告'), ('mrna_sec', 'Moderna SEC公告'), ('sgov', 'iShares SGOV官方收益率')]],
}
items = copy.deepcopy(company['items'])
items[0]['title'] = 'NVDA新增治理风险，继续观察正式调查进展'
items[0]['judgment'] = '继续观察，尚无可量化财务冲击或新的安全边际结论；不依据未查明事项改写盈利预测，也不把未来可能出现的股价跌幅当作低估证明。'
company_sections = copy.deepcopy(company['sections'])
call_url = 'https://nvidianews.nvidia.com/news/nvidia-sets-conference-call-for-third-quarter-financial-results-6928873'
company_sections[0]['paragraphs'].append('后续公司事件（在本周窗口之外）：10/28官方公告安排11/17约16:20 EST发布FY2027 Q3结果、17:00 EST召开电话会，对应北京时间11/18约05:20、06:00。周末声明未提前给出该季度结果或新指引。')
company_sections[0]['sources'].append({'title': 'NVIDIA 10/28公布的Q3业绩时间安排', 'url': call_url})
social_sections = copy.deepcopy(social['sections'])
social_sections[0]['paragraphs'] = [
    '唯一入选线索来自r/investing原帖：11/9 06:52:18北京发布，正文与实质评论已读取；随后回查NVIDIA 11/8董事会正式声明。官方页仅列日期，原帖时间不能当作公告发布时间。新增已核事实见NVDA治理风险研究。',
    '评论对过去股价变化的因果猜测未核实，不采用；调查启动不等于指控成立，也不等于调查已经排除风险。',
    'Reddit本次仅部分覆盖：investing RSS取得25帖，其他5社区RSS限流，六社区Top日窗为旧缓存。昨日STRL与模型路由不重复；发电采购二手转述未获原始交易确认，不列为已核事实。',
]
social_sections[0]['sources'].append({'title': 'r/investing原帖（线索来源；仅采用已获官方核验部分）', 'url': 'https://www.reddit.com/r/investing/comments/1xrbjp6/'})
brief = {
    'schema_version': 1, 'report_date': '2026-11-09', 'market_session': '2026-11-06', 'reviewed_at': now,
    'summary': '⚠️ NVDA董事会启动独立调查，新增治理不确定性，财务影响尚未量化；继续观察，不据此认定低估。美股无新收盘，今晚北京时间22:30恢复常规交易。',
    'items': items,
    'sections': [session] + company_sections + [cal] + social_sections + retained,
}

seed_path = SITE / 'worker/seed.json'
seed = read(seed_path)
before = copy.deepcopy(seed)
assets = [a for g in seed['catalog']['groups'] for a in g['assets']]
assert len(assets) == 43 and sum(a['kind'] == 'fund' for a in assets) == 17
assert not {'QQQ', 'PDD', 'DDL', 'BABA', 'XPEV', 'TCEHY', 'KWEB'} & {a['symbol'] for a in assets}
nvda = next(a for a in assets if a['symbol'] == 'NVDA')
nvda['research_status'] = '11/8新增治理风险，调查结论与财务影响待核；估值未完成'
nvda['next'] = '核董事会/监管或SEC更新、管理职责和客户订单；11/17财报后再核经营指引，未取得量化证据不重写盈利模型。'
nvda['facts']['governance_event'] = copy.deepcopy(company['card_updates'][0]['facts'])
nvda['facts']['fact_lines'] = [
    '治理事项：11/8公告、11/9复核。董事会宣布独立调查，由独立董事委员会监督、外部独立法律顾问协助；CEO表示配合。',
    '董事会表示目前没有理由认为国家安全或公司机密已受损，仍信任领导团队；这是当时声明，调查结论尚未形成。',
    '两份官方声明未量化订单、收入、利润或现金损失，也未宣布业绩指引调整。11/6报价早于此事件，不能作为公告后的市场反应。',
]
nvda['facts']['risks'] = ['新增治理与关键人物不确定性；客户AI投入兑现、竞争、供应和出口限制、估值及收入集中。']
nvda['facts']['gaps'] = ['调查结果、潜在监管后果及最终经营影响未定；最新财务分母与保守情景估值尚未完成，本次治理复核不等于重估。']
existing_urls = {s['url'] for s in nvda['facts']['sources']}
for source in company['card_updates'][0]['sources']:
    if source['url'] not in existing_urls:
        nvda['facts']['sources'].append(dict(source, asof='2026-11-08公告；2026-11-09复核'))
old_assets = {a['symbol']: a for g in before['catalog']['groups'] for a in g['assets']}
assert all(a == old_assets[a['symbol']] for a in assets if a['symbol'] != 'NVDA')
assert all(nvda[k] == old_assets['NVDA'][k] for k in ('quote', 'extended'))
assert seed['risk_metrics'] == before['risk_metrics']
save(SITE / 'worker/daily-brief.json', brief)
save(seed_path, seed)
save(HERE / 'daily_brief_published_candidate.json', brief)
save(HERE / 'nvda_card_published_candidate.json', nvda)
save(HERE / 'assembly_audit.json', {'reviewed_at': now, 'report_date': brief['report_date'], 'market_session': brief['market_session'], 'asset_count': 43, 'headlines': len(items), 'sections': len(brief['sections']), 'changed_research_symbols': ['NVDA'], 'quotes_changed': False, 'historical_metrics_changed': False, 'private_data_imported': False})
save(HERE / 'nvda_calendar_crosscheck.json', {'checked_at': now, 'source': call_url, 'announcement_date': '2026-10-28', 'publication_approx_et': '2026-11-17T16:20:00-05:00', 'call_et': '2026-11-17T17:00:00-05:00', 'publication_approx_beijing': '2026-11-18T05:20:00+08:00', 'call_beijing': '2026-11-18T06:00:00+08:00', 'read_scope': 'Complete official announcement opened by root; resolves dynamic events page gap; outside upcoming seven-day window'})
print(json.dumps({'date': brief['report_date'], 'headlines': len(items), 'sections': len(brief['sections']), 'changed_asset': 'NVDA'}, ensure_ascii=False))
