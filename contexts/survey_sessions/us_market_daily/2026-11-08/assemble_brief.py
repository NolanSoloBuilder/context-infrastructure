"""Assemble public weekend research; never import private portfolio data."""
from pathlib import Path
import copy
import json
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SITE = ROOT / 'adhoc_jobs/us_market_site'

def read(path):
    return json.loads(path.read_text())

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

previous = read(HERE / 'daily_brief_before.json')
company = read(HERE / 'public_company_sections.json')
sources = read(HERE / 'public_source_sections.json')
session = read(HERE / 'public_session_section.json')
reviewed_at = datetime.now(timezone.utc).isoformat()
retained = [copy.deepcopy(x) for x in previous['sections'] if x['title'].startswith(('11/5估值专题留存', 'FDE上市公司地图', 'AI应用专题'))]
assert len(retained) == 12
for x in retained:
    x['paragraphs'] = ['本节为11/5估值留存，详细模型采用11/4收盘；不代表11/8已重估，当前行情请看标的卡片的实际日期。' if p.startswith('估值复核日11/5，详细模型中的报价基准为11/4；') else p for p in x['paragraphs']]
    if not x['title'].startswith('11/5'):
        x['paragraphs'].insert(0, '既有专题留存，沿原研究与披露日期；本次周末未重做该公司估值，不因行情自动刷新而改写研究日期。')
mrna = copy.deepcopy(next(x for x in previous['sections'] if x['title'].startswith('MRNA现金桥')))
mrna['title'] = '11/7研究留存｜' + mrna['title']
mrna['paragraphs'].insert(0, '以下为11/7已完成的Q3现金桥，今天无新增核验结论。')
capital = copy.deepcopy(next(x for x in previous['sections'] if x['title'].startswith('Google与SOFI｜11/5资本桥')))
capital['title'] = '既有研究留存｜Google与SOFI融资及资本桥（11/5披露、11/7复核）'
capital['paragraphs'].insert(0, '本节仅保留原资本桥及明确标注11/6的价格参照；本次没有重做Google的TPU回款模型或SoFi正常化盈利估值。')
capital['paragraphs'] = [p.replace('Google：本次推进的是融资资本桥。', 'Google：11/5推进的是融资资本桥。') for p in capital['paragraphs']]
brief = {
    'schema_version': 1,
    'report_date': '2026-11-08',
    'market_session': '2026-11-06',
    'reviewed_at': reviewed_at,
    'summary': '⏳ 周末继续观察。伯克希尔Q3已公布：回购加大，但保险成本上升；汇率也放大了经营利润降幅，现价安全边际尚未证实。最近收盘11/6，下次交易11/9。',
    'items': company['items'],
    'sections': [session] + company['sections'] + sources['sections'] + retained + [mrna, capital],
}
brief['items'][0]['sources'] = [dict(s, title=s['title'].replace('（主线本次读取）', '（11/8读取，价格截至11/6）')) for s in brief['items'][0]['sources']]
for section in brief['sections']:
    for source in section.get('sources', []):
        source['title'] = source['title'].replace('（主线本次读取）', '（11/8读取，价格截至11/6）')
    if section['title'] == 'BRK.B｜本次核验边界':
        section['paragraphs'][1] = '本次读取的11/6盘后572.50美元（19:59 EST时刻参考）发生在财报之前，不是财报后价格反应；周末不新增常规行情或回撤触发。11/6收盘570.89美元来自11/8重新读取的StockAnalysis历史页；Yahoo本次请求受限，未完成新的跨源报价核验。'

seed_path = SITE / 'worker/seed.json'
seed = read(seed_path)
before = copy.deepcopy(seed)
assets = [a for g in seed['catalog']['groups'] for a in g['assets']]
assert len(assets) == 43 and sum(a['kind'] == 'fund' for a in assets) == 17
assert 'QQQ' not in {a['symbol'] for a in assets}
assert not {'PDD', 'DDL', 'BABA', 'XPEV', 'TCEHY', 'KWEB'} & {a['symbol'] for a in assets}
card = next(a for a in assets if a['symbol'] == 'BRK-B')
update = company['card_updates'][0]
card['research_status'] = update['research_status']
card['next'] = update['next']
card['facts']['financial_date'] = '2026-09-30'
card['facts']['research_reviewed_at'] = reviewed_at
card['facts']['fact_lines'] = [
    '2026Q3，财务截至9/30、11/7发布、11/8复核：税后经营利润127.05亿美元（同比−5.8%），GAAP归母净利221.12亿美元。经营利润包括投资利息、股息及权益法收益。',
    'GEICO税前承保利润9.82亿美元，综合成本率91.4%；集团经营同比减少7.80亿中，非美元债汇率摆动为6.74亿。仅剔该项后同比约−0.81%，不代表完成全部正常化调整。',
    '9/30集团现金及等价物＋另列短期国库券毛额3774.35亿美元；保险及其他业务扣未结算国库券应付后3522.80亿。未扣全部债务、保险责任与资本需求，均不称可分配净现金。',
    'Q3回购约96亿美元，前三季账面144.09亿、现金支付137.57亿；Q3股票组合净卖出4.26亿，与自家股票回购分开。',
    '11/6财报前收盘570.89美元，按9/30精确B等价股数与归母净资产P/B约1.60；前三季经营利润简单年化对应约24.6倍。仅作可复算估值参照，完整分部估值未完成。',
]
card['facts']['notes'] = ['回购均价不是内在价值或买入底线；经营利润资本化后再全额加投资资产会重复计价。', '行情刷新时间与财务及研究日期分别保留；11/6盘后发生在11/7财报之前。']
card['facts']['risks'] = ['保险赔付、保费定价与投资收益率；经营周期、能源责任及资本配置。']
card['facts']['gaps'] = ['最新逐项13F权重未核，完整分部估值未完成；公司官网已取得完整Q3 10-Q，SEC recent本次尚未见对应新入库条目。']
card['facts']['sources'] = [dict(x, asof='2026Q3（9/30），11/7发布、11/8复核' if '3rdqtr26' in x['url'] or 'nov0726' in x['url'] else '2026Q2（6/30），11/8用于单季差分') for x in update['sources']]
old_assets = {a['symbol']: a for g in before['catalog']['groups'] for a in g['assets']}
assert all(a == old_assets[a['symbol']] for a in assets if a['symbol'] != 'BRK-B')
for k in ('quote', 'extended'):
    assert card[k] == old_assets['BRK-B'][k]
assert seed['risk_metrics'] == before['risk_metrics']
save(SITE / 'worker/daily-brief.json', brief)
save(seed_path, seed)
save(HERE / 'daily_brief_published_candidate.json', brief)
save(HERE / 'brk_card_published_candidate.json', card)
save(HERE / 'assembly_audit.json', {'reviewed_at': reviewed_at, 'market_session': brief['market_session'], 'asset_count': len(assets), 'headline_count': len(brief['items']), 'sections': len(brief['sections']), 'changed_research_symbols': ['BRK-B'], 'quotes_changed': False, 'risk_metrics_changed': False, 'private_data_used_in_public_assembly': False})
print(json.dumps({'date': brief['report_date'], 'session': brief['market_session'], 'headline_count': len(brief['items']), 'section_count': len(brief['sections']), 'asset_count': len(assets)}, ensure_ascii=False))
