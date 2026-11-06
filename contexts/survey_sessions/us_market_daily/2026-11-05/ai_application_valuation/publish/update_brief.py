import json
from datetime import datetime, timezone
from pathlib import Path
from sections import NOW, GEHC, CGNX, FDE, NOW_SOURCES, CRM_SOURCES, GEHC_SOURCES, CGNX_SOURCES, src

WORKSPACE = Path('/Users/xuhao/Documents/Other/context-infrastructure')
SITE = WORKSPACE/'adhoc_jobs/us_market_site'
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
nc = json.loads((ROOT/'now_crm/valuation_inputs_and_results.json').read_text())['companies']
c = nc['CRM']
assert 183 < c['scenarios']['base']['fair_value_per_share'] < 185, 'Require reviewed acquisition-value bridge'
def fair(name): return c['scenarios'][name]['fair_value_per_share']
crm_values = '/'.join(f'{fair(x):.2f}' for x in ['bear','base','bull'])
crm_margin = fair('base')*.8
crm_strict = fair('bear')*.8
CRM = {"title": "四股估值②｜CRM：表面13.6倍PE，剔浮盈并保留SBC后约23.8倍", "paragraphs": [
"营业范围：销售/客服CRM、营销、电商、Slack和数据整合，Agentforce在这些流程中执行任务。11/4常规收盘227.11美元，Yahoo与第二来源一致。最新完整财务为FY2027Q2截至7/31、8/26发布；截至10/31季度完整财报本次尚未取得，不能把7月底余额称为今日资产负债表。",
"Q2收入113.45亿美元，包含Informatica约4.56亿；不能把全部总增长称为同口径AI增长。GAAP营业利润23.31亿＋SBC9.04亿＋并购摊销5.22亿＋重组/收购1.15亿＝调整营业利润38.72亿。GAAP EPS4.29与调整EPS5.90都包含投资收益影响；上半年投资净收益31.71亿不是Agentforce收入。",
"盈利纠偏：管理层FY27（截至2027/1/31）调整EPS指引中点16.69对应13.61倍PE。但从GAAP指引10.23减已知投资浮盈税后额，再加回并购摊销/重组并保留SBC经济成本，得到前瞻正常化代理9.53美元：10.23−31.71亿×76.5%÷8.38亿股＋(2.45+0.42)×76.5%。对应约23.83倍；仍是研究者对展望的修正，不是已实现EPS，整合费持续性和未来利息仍有不确定性。",
"TTM现金桥：CFO157.50亿−现金capex5.96亿＝标准FCF151.54亿；减SBC36.65亿与持续融资义务本金6.12亿，得到108.77亿股东现金代理（约5.79%市值收益率，标准FCF约8.07%）。再以现金付息4.01亿、利息收入4.26亿和23.5%税率作现金净利息调整，得108.57875亿近似FCFF；相关融资/租赁债务不再加进净债务重复扣。",
"回购与净债务：7/31现金及证券114.03亿、有息本金395亿，历史净债务280.97亿。250亿美元债务融资ASR已经体现在这份债务和初始股份中，不能再扣一次现金。基准分母采用管理层下一季稀释股指引8.27亿（前季实际8.21亿），ASR最终股数仍待核。回购提升EPS不等于经营利润按同比例改善。",
"并购要同时记付款和取得价值：Fin 9/10、Contentful 9/1已完成，已披露现金约36亿/15亿。资本桥暂预留合计51亿现金，将净债务代理推至331.97亿；这是模型预留，不是最新已核余额。另单列所取得业务价值25.5/51/76.5亿（成本0.5/1/1.5倍），不把它重复塞进原业务增长。目标现金流不全，购买成本只是敏感性占位，绝非独立估值。若目标价值只计0/25.5/51亿，基准每股约177.76/180.85/183.93。",
"其他资本缺口：Loops 11/2完成但价格未核；10/20拟购Braze的56.6亿美元是企业价值，预计FY28完成，不当成已支付现金。新的经营现金、分红、目标现金、购买价分配及其他承诺尚待完整新10-Q。战略投资账面113.24亿未计基准，按账面全加回的机械敏感性约+13.69美元/股，未证明税后可变现价值。",
"十年DCF：起始owner FCFF95/104.2356/120亿美元；基准从TTM代理保留4%现金税/营运资金缓冲，乐观起点要求未来兑现。前五年增长3%/7%/10%，后五年2%/4%/6%，折现率11%/10%/9%，永续2%/2.5%/3%。先算经营价值，再扣模型净债务、加上述已购业务价值并除8.27亿股。增长均指扣SBC后的经营现金流，不是收入。",
f"结果：保守/基准/乐观约{crm_values}美元；基准八折{crm_margin:.2f}美元，严格保守八折{crm_strict:.2f}美元。当前227.11尚无基准折扣。基准值若另加战略投资全部账面约197.62美元，仍不能消除目前估值与并购核验缺口；把乐观情景当目标价会过度乐观。",
"最强正证是客户基础、工作流与存量现金生成能力；反证是Agentforce口径扩展/收购贡献、席位收入被替代、持续并购和更高债务负担。先核ASR最终分母、新10-Q净债务与付费消费回款；若有机增速、每股扣SBC现金流未改善，或额外资本承诺显著增加，条件价必须下修。原业务与新增收购业务价值拆开后再更新，不能只看价格跌幅。",
], "sources": CRM_SOURCES + [src("Loops交易更新", "https://www.salesforce.com/news/stories/salesforce-signs-definitive-agreement-to-acquire-loops/")]}

quotes = {"title": "估值报价核验｜11/4常规收盘与盘后分开，美元", "paragraphs": [
"四股估值统一使用2026-11-04美国常规收盘，16:00 EST对应北京11/5 05:00：NOW108.81、CRM227.11、GEHC85.81、CGNX53.06美元。本次Yahoo完整日线与分别重新读取的StockAnalysis页面收盘精确到美分一致；GEHC另核Investing。均为第三方，可能共用底层供应商，不冒称交易所独立审计。Yahoo首次本次日线采集11/5 02:48:56 UTC，分钟数据02:52:16 UTC。",
"盘后参考与常规分栏口径：NOW Yahoo108.50，11/4 19:57:31 EST（北京11/5 08:57:31）；第二源108.50，19:59 EST（北京08:59）。CRM Yahoo226.12，19:57:16 EST（北京08:57:16）；第二源227.68，19:59 EST（北京08:59），存在差异。",
"GEHC Yahoo85.75，11/4 19:59:12 EST（北京11/5 08:59:12）；第二源86.40，19:59 EST（北京08:59），存在差异。CGNX Yahoo50.99，19:13:19 EST（北京08:13:19）；第二源50.60，19:56 EST（北京08:56），时点不同，不能说完全一致。两者较自身常规53.06分别约−3.90%和−4.64%。",
"上述Yahoo分钟柱均为零成交量延续参考，不声称该时刻有新成交。采集时盘后时段已结束，也不能称这些值是最终盘后成交；四股估值均不用盘后价。11/5美国下一交易日盘前在本次复核时尚未开始。未含券商20:00–04:00夜盘。",
], "sources": [src(f"{s} Yahoo日线", f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?range=5d&interval=1d") for s in ['NOW','CRM','GEHC','CGNX']] + [NOW_SOURCES[-1],CRM_SOURCES[-1],GEHC_SOURCES[-1],CGNX_SOURCES[-1]]}

overview = {"title": "估值总览与口径｜合理价值、基准折扣、保守压力值分开", "paragraphs": [
f"同日常规收盘 → 基准现金流价值 → 基准价值八折研究价（美元）：NOW108.81 → 83.30 → 66.64；CRM227.11 → {fair('base'):.2f} → {crm_margin:.2f}；GEHC85.81 → 68.68 → 54.94；CGNX53.06 → 31.98 → 25.58。当前四家均没有达到本模型基准价值八折，不能认定已低估。",
"两条优先研究线：GEHC在盈利法下接近合理，但需证实利润能变为现金；CRM现有现金生成较强，但需要剔浮盈、核借债回购与并购后的每股价值。NOW商业增长更快，当前需更高现金增长兑现；CGNX现价接近本次乐观现金情景。这个顺序是核验价值与风险的顺序，不是收益预测或仓位分配。",
f"‘20%安全边际’在本专题只定义为研究估值×0.8，不是最大亏损保证，也不是对52周高点回撤20%。若要求保守情景仍打八折，条件价分别NOW30.91、CRM{crm_strict:.2f}、GEHC27.99、CGNX16.25美元；这些严苛压力结果不等于会跌到或应该无限等待。任何基本面变坏都会改变估值本身。",
"主要现金流模型把SBC视为股东成本，只扣一次；以现金净利息代理还原经营现金流后再处理净债务，不把含债务利息的现金流与全额债务简单双扣。模型保留了现金利息、税项和收购数据缺口，不能把小数精度误认为估值精度。折现率、终值增速及PE均为明示研究假设，尚未以完整同业/历史分位校准。",
"本次完成四家条件估值及FDE业务梳理；不把新公司自动加入现有17项行情清单，15%/25%提醒仍只适用于QQQM、VOO、BRK.B。本专题研究价格不会自动触发交易或替换提醒合同。",
], "sources": [NOW_SOURCES[0],CRM_SOURCES[0],GEHC_SOURCES[1],CGNX_SOURCES[0]]}

path=SITE/'worker/daily-brief.json'
old=json.loads(path.read_text())
(HERE/'brief_before.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
oldsections=[p for p in old['sections'] if p['title']!='Cognex：估值敏感性、税项与收购资金']
# Prior daily market research remains, clearly dated; it is not re-labelled as newly verified.
prior=[]
for item in old['items'][1:]:
    prior.append({"title":"今日早间研究续存｜"+item['title'],"paragraphs":["以下保留11/5早间原复核口径，本专题未重新核验这些证券行情；不是新的报价或触发。"]+[f"{k}：{item[v]}" for k,v in [('事实','fact'),('影响','implication'),('判断','judgment'),('反证','counter'),('下次','next')]],"sources":item['sources']})
items=[
{"title":"四股重估：现价均未给出基准八折", "fact":"11/4常规收盘：NOW108.81、CRM227.11、GEHC85.81、CGNX53.06美元；已逐项核对本次第三方行情与最新财报。", "implication":"SBC、投资浮盈、借债回购和并购资本支出改变了股东真正得到的利润。AI落地业务成立，不等于现价便宜。", "judgment":f"条件基准DCF：NOW约83、CRM约184、GEHC约69、CGNX约32美元；对应基准八折约67、147、55、26美元。均为研究条件价，详细精确值和假设见下方。", "counter":"更快增长、利润率提升、更低资金成本或收购兑现会提高价值；宽情景区间表明不确定性高，不能用保守模型断言必跌。", "next":"优先核CRM最新资本桥、GEHC现金转化；NOW看扣SBC每股现金，CGNX看今晚21:30电话会和RealSense条款。本次不改变原提醒阈值。", "sources":[NOW_SOURCES[0],CRM_SOURCES[0],GEHC_SOURCES[1],CGNX_SOURCES[0]]},
{"title":"容易误判的便宜：CRM的13.6倍与GEHC的17.2倍", "fact":"CRM管理层调整EPS含口径差异，保留SBC并剔已知浮盈后，前瞻盈利代理约9.53、现价约23.8倍。GEHC全年调整EPS指引中点5.00、现价约17.2倍。", "implication":"CRM不是简单的低PE软件股；GEHC盈利基准约90美元，而现金流基准约69美元，两法尚未收敛。", "judgment":"CRM与GEHC值得优先继续核验估值修复，但当前均不确认低估。GEHC约72美元仅有盈利法八折，现金法要约55美元；不把两法平均出一个看似确定的买点。", "counter":"持续整合费用可能下降、营运资金会回流、战略投资有价值，因此保守扣减也可能低估；这些需用新现金流与资产证据验证。", "next":"CRM新10-Q、ASR最终分母与收购资金；GEHC库存/合同资产回款、剔退款现金流及2027指引。报价和模型只按本次研究日期有效。", "sources":[CRM_SOURCES[2],CRM_SOURCES[3],CRM_SOURCES[5],GEHC_SOURCES[0],GEHC_SOURCES[1]]},
{"title":"FDE已有上市公司：交付模式决定利润归谁", "fact":"已核PLTR、NOW、CRM、ACN、EPAM、GLOB的官方FDE岗位、产品或合作证据；本次所读财报均未单列FDE收入/利润。", "implication":"前三家更多以工程交付带动自有平台，后三家更多跨平台工程实施。客户愿意付费不等于服务商能获得软件利润率。", "judgment":"先看工程师离场后谁仍持续收费：平台复用、续费和每股现金改善，比FDE招聘数量更有投资意义。FDE名单是研究候选，不是低估名单。", "counter":"EPAM Q2约78%收入仍按工时；GLOB AI ARR增长与公司毛利率下降同时存在；NOW专业服务当季成本高于收入。", "next":"核收入/员工、实施周期、固定价项目毛利、续费及ARR转收入；EPAM今晚北京21:00进入Q3发布/电话会窗口，本次不提前引用结果。", "sources":[FDE['sources'][0],FDE['sources'][2],FDE['sources'][3],FDE['sources'][7],FDE['sources'][9]]}]
new={**old,"reviewed_at":datetime.now(timezone.utc).isoformat(),"summary":"🔎AI落地估值专题已更新：四家公司当前均未达到本次基准估值八折。优先继续核验CRM的资本配置与GEHC的现金转化；NOW、CGNX需要更强增长来支撑现价。FDE已有六家上市样本，但属于交付模式，不是已单列财务的新行业。","items":items,"sections":[overview,NOW,CRM,GEHC,CGNX,FDE,quotes]+prior+oldsections}
path.write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n')
(HERE/'published_brief.json').write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n')

sp=SITE/'worker/seed.json';seed=json.loads(sp.read_text())
assets=[a for g in seed['catalog']['groups'] for a in g['assets']]
assert len(assets)==17 and not any(a['symbol']=='QQQ' for a in assets)
cg=next(a for a in assets if a['symbol']=='CGNX')
cg['personal_note']='机器视觉与机器人感知研究；11/5条件DCF基准约32美元，当前未确认低估。增长、收购与SBC现金成本见当日专题。'
cg['facts']['gaps']=['已完成条件现金流估值，尚缺RealSense独立利润、交割确认、Q3完整10-Q与电话会；目标价值仅为购买成本敏感性。']
cg['facts']['notes']=['RealSense收入8000万–9000万美元为2026展望，非已确认交付收入。','2026-11-05专题：独立主营DCF加收购资本桥约20/32/53美元，基准八折约26美元；均非自动买价，行情刷新不会自动重估。']
cg['next']='11/5北京21:30电话会及完整10-Q；核RealSense交割、目标盈利、留任/RSU与主营现金流，变化后重估。'
sp.write_text(json.dumps(seed,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({"reviewed_at":new['reviewed_at'],"sections":len(new['sections']),"watchlist_count":len(assets),"CRM_base":fair('base'),"CRM_base_discount20":crm_margin}))
