"""Assemble reviewed public research; no private portfolio input or publication."""
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

P=Path(__file__).resolve().parent
SITE=P.parents[3]/'adhoc_jobs/us_market_site'
def read(path):return json.loads(path.read_text())
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def source(title,url):return {'title':title,'url':url}
M={m['symbol']:m for m in read(P/'metrics.json')}
seed=read(SITE/'worker/seed.json')
assets={a['symbol']:a for g in seed['catalog']['groups'] for a in g['assets']}
previous=read(SITE/'worker/daily-brief.json')
company=read(P/'public_company_sections.json')
macro=read(P/'public_macro_sections.json')
social=read(P/'public_source_sections.json')
alert=read(P/'public_alert_section.json')
preserved=[deepcopy(s) for s in previous['sections'] if s['title'].startswith(('11/5估值专题留存｜','FDE上市公司地图','AI应用专题'))]
q=M['QQQM']
items=[{
 'title':'🔎 QQQM回撤13.97%；11/5曾触及15%已补核',
 'fact':'11/6常规收270.22美元，距10/6盘中高点314.11回撤13.97%。第二源已修正11/5收盘至266.85，当日超过15%现获补核；11/6是反弹回到接近档，不是新向下跨档。',
 'implication':'纳指100反弹未消除估值与盈利兑现风险；10月非农新增16.5万、前两月上修8.4万，收入基础尚稳，但2年/10年美债收益率升至4.51%/4.86%，估值折现仍有压力。',
 'judgment':'继续观察，暂缓加快追加；距15%价266.99美元还需跌1.19%，距离为1.03个百分点。反弹不足以确认趋势修复。',
 'counter':f"QQQM较200日线仍低{-q['vs_ma200_pct']:.2f}%，成交量约此前20日均量{q['volume_vs_prior20']:.2f}倍；12项行业观察仅4项上涨。反证是指数站回200日线且行业广度持续改善。",
 'next':'11/10北京时间21:30 CPI；观察QQQM在266.99美元附近的收盘、200日线与行业广度。15%/25%仅为研究条件，盘后参考不更新收盘档位。',
 'sources':alert['sources'][:2]+[source('BLS 11/6就业报告','https://www.bls.gov/news.release/empsit.nr0.htm'),source('美国财政部每日收益率','https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value=202611&type=daily_treasury_yield_curve')]
},deepcopy(company['items'][0]),{
 'title':'FDE看现金兑现：EPAM回购授权不等于已花现金',
 'fact':'11/6新讨论重提11/5披露：新增15亿美元是回购授权；拟11/9当周5亿美元加速回购尚待执行。前九个月实际回购4.89亿美元，高于同期经营现金流2.501亿。',
 'implication':'扩大AI交付团队可能增加收入，也需要人力和营运资金；回购若依靠现金储备或信贷，并不能证明FDE已带来可持续现金利润。',
 'judgment':'FDE仍是值得研究的上市公司方向，但EPAM尚未完成正常化估值；回购金额和AI叙事都不足以确认低估。',
 'counter':'季度现金流受回款季节性影响，授权也不代表必定全部执行；若后续现金转化、每员工收入与考虑股权薪酬稀释后，回购仍使实际流通／稀释股数下降，会削弱当前担忧。',
 'next':'核5亿美元ASR实际执行、借款与现金余额、FDE付费项目和固定价利润；NOW/CRM/GEHC/CGNX继续按已披露的条件模型观察，不把软件和工程服务套同一估值。',
 'sources':[source('EPAM 11/5官方Q3业绩与资本配置','https://investors.epam.com/news/news-details/2026/EPAM-Reports-Results-for-Third-Quarter-2026/default.aspx'),source('11/6 Reddit新讨论及实质评论','https://www.reddit.com/r/stocks/comments/1xpf1ot/epam_came_up_with_new_15b_cash_burning/')]
}]
items[1]['judgment']='11/6收254.19美元、日涨5.27%，经营改善但尚不能确认低估；完整管线估值与安全边际仍待完成。'
items[1]['sources'].append(source('MRNA 11/6第二源收盘254.15美元','https://stockanalysis.com/stocks/mrna/history/'))

valuation_paras=['价格更新至美国11/6常规收盘，美元；模型沿11/5已核情景，未把行情刷新当重新估值。基准价值不是保证可实现的价格；八折研究价仅为模型折扣，不是新增交易规则。']
for s in ['NOW','CRM','GEHC','CGNX']:
 v=assets[s]['valuation'];p=M[s]['close']
 valuation_paras.append(f"{s}：收盘{p:.2f}、日{M[s]['day_pct']:+.2f}%；现金流基准{v['base_value']:.2f}、基准八折{v['discount_price']:.2f}美元；到八折价仍需变化{100*(v['discount_price']/p-1):+.1f}%。{v['judgment']}")
valuation_paras+=['GEHC盈利法基准90美元、八折72美元，是另一组正常化EPS假设；现金法68.68/54.94与其不收敛，不能简单平均后宣布便宜。','本次四股均高于现金流基准八折条件。CRM当日−3.94%不改变资本桥约束；CGNX的RealSense交割与现金留任仍需核实。价格下降本身不是估值分母改善。','第二源收盘NOW101.98、CRM213.65、GEHC82.39、CGNX47.70，分别与主序列相差0.01/0/0.01/0.08美元；并列说明，不称完全一致。']
valuation={'title':'估值报价更新｜11/6四股仍未到现金流折扣条件','paragraphs':valuation_paras,'sources':[source(s+'带日期历史收盘','https://stockanalysis.com/stocks/'+s.lower()+'/history/') for s in ['NOW','CRM','GEHC','CGNX']]}
old_google=next((deepcopy(s) for s in previous['sections'] if s['title'].startswith('Google与SOFI｜')) ,None)
if old_google:
 old_google['title']='Google与SOFI｜11/5资本桥留存，11/6价格复核'
 old_google['paragraphs'][0]='11/5已核融资事实留存，非今日新增公告。'+old_google['paragraphs'][0]
 old_google['paragraphs'][1]='GOOGL公司研究11/6报价284.78美元，第二源284.68；不混用GOOG C类报价。10/30完整Q3模型及11/5反向DCF仍是旧资本/经营假设下的条件敏感性，尚未完成融资后TPU营运资金重估，旧研究价继续暂停。'
 old_google['paragraphs'][2]='11/5已核10-Q事实留存，非今日新增申报。'+old_google['paragraphs'][2]
 old_google['paragraphs'][3]=f"SOFI 11/6报价16.21美元、第二源16.20。沿9/30每股有形净资产7.48美元，P/TBV代理{16.21/7.48:.2f}倍；未因跌幅确认低估。正常化EPS及资本回报估值仍未完成。10/15现金偿债与债务减少要成对考虑；下一步核贷款公允价值/销售留存、存款成本、资本回报及真实股数。银行存款属于经营资金，不用工业企业净现金DCF。"
sections=[alert,valuation]+preserved+read(P/'market_sections.json')+[read(P/'public_extended_section.json')]+macro+company['sections']+([old_google] if old_google else [])+social['sections']
brief={'schema_version':1,'report_date':'2026-11-07','market_session':'2026-11-06','reviewed_at':datetime.now(timezone.utc).isoformat(),'summary':'继续观察，暂缓加快追加。QQQM回到13.97%回撤，11/5达到15%已补核；Moderna季度盈利仍需现金回收验证；FDE研究继续区分交付增长与股东现金回报。','items':items,'sections':sections}
write(SITE/'worker/daily-brief.json',brief)

# Replace stale current facts; preserve historically dated clinical context only.
u=company['card_updates'][0];a=assets['MRNA'];facts=deepcopy(u['facts'])
facts.update(name='Moderna',type='个股／mRNA生物制药',strategy='mRNA生物制药：呼吸道疫苗与肿瘤管线。',business='商业化疫苗及研发管线；临床、审批、上市销售与盈利分阶段核查。',status=u['research_status'],next=u['next'])
facts['notes'].append('10/22披露的肿瘤三期临床结果是历史证据；完整管线估值仍须审批概率、利润分成、制造和商业化成本，不直接用临床风险比估收入。')
facts['risks'].append('Arbutus/Genevant上诉最高13亿美元潜在支付尚未计提；与10/28无需付款的GSK和解不同。')
a.update(facts=facts,next=u['next'],research_status=u['research_status'])
a['personal_note']='Q3季度盈利与融资后现金需分开；经营回款和风险调整管线估值继续核查。'

a=assets['QQQM'];a['next']='11/6回撤13.97%；11/5达到15%已于11/7补核，非11/6新跨档。15%价266.99美元；继续核200日线、行业广度与11/10 CPI。'
a['facts']['gaps']=['最新官方持仓权重仍缺；不把其他同指数基金权重复制为QQQM精确权重。']
assets['VOO']['next']='11/6收675.99美元，高点718.47（10/6），回撤5.91%；未接近15%档。关注11/10 CPI及200日线得失。'
assets['BRK-B']['next']='官方计划北京时间11/7 21:00发布Q3；届时核经营利润、现金、赔付与回购。11/6回撤2.63%，按单一公司研究。'
a=assets['SOXX'];a['next']='3:1拆股历史已获提供方统一，11/6恢复指标；收136.53与第二源136.43仍有差异，关注行业盈利周期。'
a['facts']['notes']=[n for n in a['facts']['notes'] if '部分历史单位混杂' not in n]
a['facts']['notes'].append('2026-11-05生效的3:1拆股，本次11/7重新采集已统一前后历史；11/5真实价格跌幅约12.15%，不使用旧混合单位的假跌幅。')
assets['XSW']['next']='11/5高低价矛盾已修正，11/6恢复指标；Yahoo收202.67与第二源202.17差0.50美元，精确收盘差异仍待核，不称完全一致。'
a=assets['SGOV'];a['facts']['notes']=[n for n in a['facts']['notes'] if '30日SEC收益率' not in n]
a['facts']['notes'].append('30日SEC收益率3.83%，截至2026-11-05，本次11/7核验；分配收益率3.63%，二者不同，均不代表未来总回报。')
for s in a['facts']['sources']:
 if s['title']=='SGOV官方SEC收益率本周复核':s['asof']='SEC收益率2026-11-05，11/7读取；其他字段各自日期'
a['facts']['sec_yield_pct']=3.83;a['facts']['sec_yield_date']='2026-11-05'
a=assets['EPAM'];a['facts']['reviewed_date']='2026-11-07'
a['facts']['fact_lines']=[n for n in a['facts']['fact_lines'] if '新增15亿美元回购授权' not in n]
a['facts']['fact_lines'].append('11/5披露新增约15亿美元回购授权；董事会9/30批准以18亿新计划替代旧计划（含原剩余2.93亿）。前九月实际回购4.89亿，高于经营现金流2.501亿。拟11/9当周5亿美元ASR尚待执行，不能把授权当支出。')
a['next']='核11/9当周ASR实际执行、回款与净股数；FDE单列收入和正常化估值仍待完成。'
write(SITE/'worker/seed.json',seed)
write(P/'public_daily_brief.json',brief)
write(P/'research_assembly_manifest.json',{'report_date':brief['report_date'],'reviewed_at':brief['reviewed_at'],'market_session':brief['market_session'],'watch_count':len(assets),'items':len(items),'sections':len(sections),'modified_research_symbols':['MRNA','QQQM','VOO','BRK-B','SOXX','XSW','SGOV','EPAM'],'retained_valuation_date':'2026-11-05','privacy':'Only public inputs; no private portfolio input.'})
print(json.dumps({'date':brief['report_date'],'items':len(items),'sections':len(sections),'assets':len(assets)}))
