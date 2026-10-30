"""Rebuild this dated reviewed snapshot only; does not fetch current data."""
import json,pathlib,datetime
from zoneinfo import ZoneInfo
root=pathlib.Path('/Users/xuhao/Documents/Other/context-infrastructure')
base=root/'contexts/survey_sessions/us_market_daily/2026-10-30';out=base/'watchlist_catalog'
load=lambda p:json.loads(p.read_text())
groups=load(root/'adhoc_jobs/us_market_daily/watchlist_groups.json')['groups']
funds={}
for n in ['fund_vanguard_semis.json','fund_roundhill.json','fund_sgov.json','fund_nasdaq.json']:
 d=load(out/n);funds.update(d.get('funds',d))
mrna=load(out/'mrna_facts.json')
metrics={r['symbol']:r for r in load(base/'metrics.json')}
for q in load(out/'new_quotes.json'):metrics[q['symbol']]=q
states=load(base/'watchlist_research.json')
postdata=load(base/'extended_quotes.json');posts={r['symbol']:r for r in postdata['observations']}
notes={
'VOO':('股票核心候选','本池中行业覆盖较广的股票核心候选。仍承担全股票市场风险，可能超过你约20%的回撤承受程度。'),
'QQQM':('成长指数候选','与VOO搭配时会增加大型成长集中度。与QQQ合并考虑预算，长期持有可比较较低费率。'),
'QQQ':('同指数对照','与你关注的QQQM暴露高度重合；流动性、价差和交易用途可比较，持有两只不会显著增加分散。'),
'SPMO':('动量因子','从标普500中筛选动量较强的股票，可能在趋势反转时快速回撤。它增加风格倾向，并不自动筛出低估公司。'),
'MAGS':('高集中卫星候选','七家公司的集中组合，会叠加QQQM及GOOGL/NVDA持股。若以后研究小额参与，应从同一股票预算中划分。'),
'VGT':('科技行业卫星候选','按信息技术行业筛选，与你的QQQM和半导体候选重叠。318只股票仍可能由少数权重股主导。'),
'SOXX':('芯片行业比较','用于与SMH比较芯片公司权重和费率；暂未验证行业估值安全边际，不因股价单价或名称认定便宜。'),
'SMH':('芯片行业比较','偏重头部芯片公司，与你关注的NVDA存在额外叠加。与SOXX比较后再研究额度，无须为了分散同时堆叠。'),
'DRAM':('高集中存储主题','前三家公司占约75%，比广泛芯片ETF更集中。与AI需求相关，也受到存储价格及扩产周期影响，不宜当作低风险核心。'),
'GOOGL':('头部重点研究','搜索、云增长与投入现金流一起评估。原入场价位暂停，财报后跌幅尚不足以证明低估；ETF已含Alphabet暴露。'),
'NVDA':('AI龙头研究','AI基础设施核心公司，也已存在于多只ETF中。直接买入会进一步增加AI资本开支及单一公司风险。'),
'RRX':('机器人供应链','机器人只是运动控制业务的一部分。现有条件估值尚未显示足够安全边际，不能为全部业务加上人形机器人溢价。'),
'CGNX':('机器视觉候选','观察视觉产品需求和并购整合，先验证盈利、现金及股数；未完成保守估值前保留候选状态。'),
'ATS':('自动化系统候选','自动化订单能否交付并收回现金比机器人题材更重要。周期、杠杆与回款风险较高。'),
'SOFI':('金融科技候选','分析数字银行信用、资金成本与资本回报。股价十几美元不代表估值低，也不能把存款当普通工业公司的净现金。'),
'BRK-B':('综合经营研究','保险、铁路、能源及投资资产共同构成价值。它是单一公司普通股，不能视作标普500指数或低风险替代品。'),
'SGOV':('美元防守候选','资金无需急用时仍可用于控制组合波动或等待分批。它是资产配置选择，当前未确认持有或采用配置。'),
'MRNA':('生物科技事件研究','加入医疗观察，但mRNA平台不等于已验证的AI商业化。临床、融资与现金消耗风险较高，完整估值尚未完成。')}
stock={
'GOOGL':dict(name='Alphabet / Google',strategy='搜索广告、云与AI平台；同时关注投入和股东现金回报。',business='Google Services、Google Cloud及Other Bets。GOOG/GOOGL按同一公司风险合并。',fact_lines=['2026Q3：经营现金流422.90亿美元，现金资本开支513.55亿美元，自由现金流−90.65亿美元（现金流差额口径）。','Q3包含52亿美元罚款付款与库存现金影响，不能把全部负现金流当作永久消耗。'],sources=[{'url':'https://www.sec.gov/Archives/edgar/data/1652044/000165204426000084/goog-20260930.htm','title':'Alphabet 2026Q3完整10-Q','asof':'季度截至2026-09-30，10/29申报'}],risks=['AI投入、搜索变现、外部算力成本、反垄断与资本回报。'],notes=['本页沿用10/30已完成的Q3核验，条件DCF仍有较宽情景差异；旧价位保持暂停。']),
'NVDA':dict(name='NVIDIA',strategy='AI计算、GPU及相关网络与软件平台。',business='数据中心与加速计算、游戏及其他业务；本页不把机器人潜在市场当作已实现收入。',sources=[{'url':'https://investor.nvidia.com/financial-info/financial-reports-and-sec-filings/default.aspx','title':'NVIDIA财务披露入口','asof':'延伸核查入口，本页未完成新财报估值'}],risks=['客户AI投入兑现、竞争、供应和出口限制、估值及收入集中。'],gaps=['本次以关注清单为范围，未重新完成最新财务分母和保守情景估值。']),
'RRX':dict(name='Regal Rexnord',strategy='电机、传动与运动控制等工业产品。',business='多元工业与运动控制业务。尚无已核验人形机器人独立收入占比。',fact_lines=['2026Q2资料：调整EPS指引中点10.60美元，经退税和股权薪酬修正后的研究分母9.71美元，仍包含收购摊销调整。'],sources=[{'url':'https://investors.regalrexnord.com/investors/ir-news/press-release-details/2026/REGAL-REXNORD-REPORTS-SECOND-QUARTER-2026-FINANCIAL-RESULTS/default.aspx','title':'Regal Rexnord Q2业绩与调整表','asof':'2026-08-05'}],risks=['工业周期、债务、收购摊销的经济成本；研究倍数有主观性。'],notes=['9.71是研究调整值，不是公司GAAP EPS。下一财报观察11/3。']),
'CGNX':dict(name='Cognex',strategy='工业机器视觉与自动化感知。',business='以机器视觉产品和相关技术为核心，核RealSense整合成本、利润及稀释。',sources=[{'url':'https://investor.cognex.com/','title':'Cognex投资者关系入口','asof':'延伸核查入口'}],risks=['制造与物流需求周期、并购整合和盈利估值。'],notes=['沿用10/30研究候选状态；关注11/4业绩。'],gaps=['未取得足够证据给出低估结论；机器人收入占比未独立确认。']),
'ATS':dict(name='ATS Corporation',strategy='自动化系统、集成与项目交付。',business='为多行业客户提供自动化解决方案；订单、交付与回款需分开。',sources=[{'url':'https://investors.atsautomation.com/','title':'ATS投资者关系入口','asof':'延伸核查入口'}],risks=['项目延期、订单周期、营运资金与杠杆；美股流动性需要单独考察。'],gaps=['本次不补写未经核验机器人收入占比或低估价。']),
'SOFI':dict(name='SoFi Technologies',strategy='数字银行、贷款、金融服务与技术平台。',business='贷款、Financial Services与Technology Platform。银行存款属于经营资金。',fact_lines=['2026Q3：净收入13.851亿美元、GAAP净利润2.410亿美元、GAAP EPS 0.18美元。','9/30有形每股净资产7.48美元；以10/29的17.61美元为分子，P/TBV约2.35倍。'],sources=[{'url':'https://investors.sofi.com/news/news-details/2026/SoFi-Reports-Third-Quarter-2026-with-Record-Net-Revenue-of-1-4-Billion-Net-Income-of-241-Million-and-Raises-Full-Year-Guidance/default.aspx','title':'SoFi Q3官方业绩','asof':'2026-10-27'}],risks=['消费信贷、贷款公允价值、监管资本、股权薪酬及稀释。'],notes=['2027调整EPS指引与GAAP历史EPS不同；资本回报压力检验不等于完整估值。']),
'BRK-B':dict(name='Berkshire Hathaway B',strategy='保险、综合经营与投资资产的公司股权。',business='保险、BNSF铁路、能源和其他经营业务，并持有上市公司及短期美债等投资。此处描述资产类型，不提供未核验的最新投资权重。',sources=[{'url':'https://www.berkshirehathaway.com/reports.html','title':'伯克希尔官方报告入口','asof':'延伸核查入口'}],risks=['保险赔付、经营周期、资产估值及资本配置。'],gaps=['本页未重新核验最新13F逐项权重，不把历史重仓名单冒充当前持仓。']),
'MRNA':{**mrna,'strategy':'mRNA生物制药：呼吸道疫苗与肿瘤管线。','business':'商业化疫苗及研发管线；个股没有ETF成分持仓。临床结果、获批、上市销售与盈利是不同阶段。','fact_lines':mrna['notes'][1:]}
}
for g in groups:
 for a in g['assets']:
  s=a['symbol'];a['kind']='fund' if s in funds else 'stock';a['facts']=funds.get(s,stock.get(s,{}));a['kind_label']=a['facts'].get('type','个股')
  a['new']=s in ['SPMO','MAGS','SOXX','DRAM','VGT','MRNA'];a['role'],a['personal_note']=notes[s];a['quote']=metrics.get(s,{})
  a['next']=mrna['next'] if s=='MRNA' else states.get(s,{}).get('next','核验估值、盈利周期、成分重叠及交易价差，再考虑是否从既定风险预算中划分。')
  ps=posts.get(s,{}).get('post',{})
  if ps.get('status')=='available':a['post_snapshot']={**ps,'capture_beijing':postdata['captured_at_beijing']}
  f=a['facts']
  if f.get('metrics',{}).get('pe') is not None:
   mt=f['metrics'];f.setdefault('notes',[]).append(f"发行人披露P/E {mt['pe']}倍、P/B {mt.get('pb')}倍（{mt['metrics_date']}）；未统一核验各基金分母口径，只作背景，不直接横比认定低估。")
  for key in ['notes','risks','gaps','sources']:f.setdefault(key,[])
result={'schema_version':1,'report_date':'2026-10-30','generated_at_beijing':datetime.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'regular_session':'2026-10-29','groups':groups,'holdings_are_user_positions':False,'approved_trades':False}
(out/'catalog.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
