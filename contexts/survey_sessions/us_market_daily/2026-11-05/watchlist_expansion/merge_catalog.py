import json,datetime
from pathlib import Path
base=Path(__file__).parent
site=Path('adhoc_jobs/us_market_site/worker')
seed=json.loads((site/'seed.json').read_text())
assets={a['symbol']:a for g in seed['catalog']['groups'] for a in g['assets']}
for a in json.loads((base/'new_assets.json').read_text()):
 if a['symbol'] not in assets: assets[a['symbol']]=a
excluded={'PDD','DDL','BABA','KWEB','QQQ'}
for s in excluded:assets.pop(s,None)
comparisons=json.loads((base.parent/'ai_application_valuation/comparison.json').read_text())
settings={
 'NOW':('当前未见安全边际；观察AI增长能否转成扣稀释后的每股现金。','扣SBC的现金流与并购资本桥；基准83.30美元，八折66.64美元。并购业务价值含情景假设。','核有机增长、订阅毛利、SBC与并购后现金回报。'),
 'CRM':('优先继续核验，暂不确认低估；资本配置是关键。','基准183.93美元，八折147.14美元。扣SBC、剔投资浮盈并纳入Fin/Contentful现金成本桥；目标价值仍是成本敏感性。','更新10-Q、ASR最终股数、收购对价和收购后现金流。'),
 'GEHC':('现金法与盈利法未收敛；优先验证现金转化。','现金流基准68.68美元，八折54.94美元；盈利法基准90美元、八折72美元，二者不可简单平均。','核库存/合同资产回款、剔退款现金流及2027指引。'),
 'CGNX':('当前更接近乐观情景；等待主营与收购兑现。','独立主营DCF加并购资本桥；基准31.98美元，八折25.58美元，目标业务价值为成本情景代理。','核完整Q3 10-Q、电话会、RealSense交割与留任/RSU成本。')}
for c in comparisons:
 s=c['symbol'];j,b,n=settings[s];assets[s]['valuation']={'reviewed_at':'2026-11-05','market_session':'2026-11-04','base_value':c['base'],'discount_price':c['base_discount20'],'judgment':j,'basis':b,'next':n};assets[s]['research_status']=j
funds=[a for a in assets.values() if a['kind']=='fund'];stocks=[a for a in assets.values() if a['kind']=='stock']
groups=[{'id':'funds','label':'ETF基金','assets':funds}]
for a in stocks:
 iid=a.get('industry_id','other');industry=a.get('industry','其他行业')
 g=next((g for g in groups[1:] if g['id']==iid),None)
 if not g:g={'id':iid,'label':industry,'assets':[]};groups.append(g)
 g['assets'].append(a)
seed['catalog']['groups']=groups;seed['catalog']['version']=4;seed['catalog']['list_reviewed_at']='2026-11-05'
for s in list(seed['risk_metrics']['symbols']):
 if s not in assets:del seed['risk_metrics']['symbols'][s]
(site/'seed.json').write_text(json.dumps(seed,ensure_ascii=False,indent=2)+'\n')
keys=['symbol','name','kind','industry_id','industry','inception_date','allow_short_history','history_start_guard','market_data_enabled','currency']
registry={'version':4,'updated_at':'2026-11-05','groups':[{'id':g['id'],'label':g['label'],'assets':[{k:a[k] for k in keys if k in a} for a in g['assets']]} for g in groups]}
Path('adhoc_jobs/us_market_daily/watchlist_groups.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
manifest={'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'count':len(assets),'funds':len(funds),'stocks':len(stocks),'symbols':list(assets),'excluded':sorted(excluded),'alert_symbols_unchanged':['QQQM','VOO','BRK-B'],'phone_scope':'已读取可见画面；继续读取其余自选中'}
(base/'integration_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in manifest.items() if k not in ['symbols']},ensure_ascii=False))
