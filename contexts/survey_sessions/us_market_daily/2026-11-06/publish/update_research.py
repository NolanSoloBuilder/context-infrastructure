import json, pathlib, datetime, copy
ROOT=pathlib.Path('/Users/xuhao/Documents/Other/context-infrastructure')
DAY=ROOT/'contexts/survey_sessions/us_market_daily/2026-11-06'
SITE=ROOT/'adhoc_jobs/us_market_site'
def read(p): return json.loads(p.read_text())
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
old=read(SITE/'worker/daily-brief.json');write(DAY/'publish/brief_before.json',old)
seed=read(SITE/'worker/seed.json'); assets={a['symbol']:a for g in seed['catalog']['groups'] for a in g['assets']}
metrics={m['symbol']:m for m in read(DAY/'metrics.json')}
company={x['id']:x for x in read(DAY/'company_sources.json')['sources']}
def source(title,url):return {'title':title,'url':url}
def csource(key,title):return source(title,company[key]['url'])
qq=[source('Yahoo QQQM日线','https://finance.yahoo.com/quote/QQQM/history/'),source('Investing带日期历史','https://ca.investing.com/etfs/qqqm-historical-data'),source('StockAnalysis不同收盘','https://stockanalysis.com/etf/qqqm/history/')]
bls=source('BLS官方11月日历','https://www.bls.gov/schedule/2026/11_sched.htm')
vix=source('Cboe VIX','https://www.cboe.com/tradable-products/vix/')
epam=csource('epam_q3_release','EPAM 11/5 Q3官方业绩')
google=[csource('goog_8k','Alphabet 11/5融资完成8-K'),csource('goog_424b2','11/4招股补充：预计净额与用途')]
soxx=csource('soxx_497','SOXX官方3:1拆股公告')
cgnx=csource('cgnx_10q','Cognex 11/5完整Q3 10-Q')
brief={'schema_version':1,'report_date':'2026-11-06','market_session':'2026-11-05','reviewed_at':now,
 'summary':'暂缓加快分批：QQQM已到15%观察线附近，但两源收盘跨线结论不同；今晚21:30非农前先核数据与风险。AI落地有实质业务，尚未普遍显示安全边际。',
 'items':[
 {'title':'🔎 QQQM到15%边界，跨档待核','fact':'11/5常规收盘，Yahoo与Investing为266.85美元，StockAnalysis为267.02美元。按各源52周高点测算回撤分别15.05%与14.99%；VIX收28.18，单日升69.66%。','implication':'QQQM单源收盘低于MA200约4.79%，成交量约此前20日均量4.67倍；这是风险显著上升，不能把临界回撤当成已见底。','judgment':'先暂停加快追加，等待收盘差异与今晚21:30非农；15%跨档暂不记为已确认触发，原阈值保持。','counter':'Yahoo与Investing一致，支持已达档；另一带日期收盘仍略未达。即使修正后确认触发，也不代表盈利或流动性风险已消失。','next':'下一交易日11/6；先核收盘修正，再看就业结果、QQQM能否收复200日线及行业跌势是否收窄。盘后仅作提前观察。','sources':qq+[vix,bls]},
 {'title':'FDE有业务，仍要看增长与现金','fact':'EPAM 11/5 Q3收入14.2643亿美元、同比+2.3%，明确扩大FDE网络；Q4收入增长指引−0.2%至+0.9%，前九月经营现金流2.501亿美元，低于去年3.720亿。','implication':'可验证上市公司在做AI交付，但还不能验证工程服务已经变成高增长软件业务；FDE收入和利润仍未单列。','judgment':'EPAM继续研究、估值待完成。NOW、CRM、GEHC、CGNX下跌后仍高于昨日现金流基准八折研究价，未确认低估。','counter':'EPAM GAAP经营利润率12.3%改善，平台复用或更高项目效率可能带来后续经营杠杆；短期现金流也受回款时点影响。','next':'核FDE订单转收入、每员工收入、回款和固定价项目利润；预计11/9当周的5亿美元ASR仍是计划，不当已回购股份。','sources':[epam,cgnx,source('四股最新报价示例：CGNX','https://stockanalysis.com/stocks/cgnx/history/')]},
 {'title':'Google发债已完成，不能只加现金','fact':'11/5 8-K确认60亿欧元优先票据发行完成；11/4招股补充估计净募资59.7亿欧元，非已核实际到账。','implication':'融资提高现金也增加负债；按预计净额与本金简单相抵，发行费用约3000万欧元。六档固定债每年票息合计约2.331亿欧元，另有7.5亿浮息债。','judgment':'继续暂停旧研究买价。此次推进融资资本桥，不因借到钱或股价回撤直接认定低估。','counter':'融资可支持高回报投资或置换旧债；最终价值取决于用途和回报，发债本身不证明业务恶化。','next':'核实际结算、偿债和汇率/对冲，再与TPU库存、应收、交付回款及资本开支联动；FCFF模型不能再把同笔利息重复扣除。','sources':google}
 ],'sections':[]}
def section(title,paragraphs,sources):return {'title':title,'paragraphs':paragraphs,'sources':sources}
brief['sections'].append(section('三项收盘提醒｜11/5价格、观察价与核验结论',[
 '价格为美元；回撤D＝100×(1−收盘价/各自滚动52周盘中高点)，窗口为(交易日−364天,交易日]。均线用拆股调整Close，不计分红；线上1/2/3年收益另用Adj Close总回报代理。两种口径不能混算。',
 'QQQM：Yahoo266.85、高314.11（10/6），D15.047%；15%/25%观察价266.9935/235.5825美元（显示266.99/235.58）。相对首档已超0.047个百分点；从现价回到15%价需上涨0.054%，两者不是同一个百分比。Investing同为266.85；StockAnalysis267.02、高314.12（10/6），D14.994%，距15%还差0.006个百分点、至目标267.002需再跌0.007%。差异虽小却跨过边界，正式状态保留11/3，本次列重点待核，不捏造跨越时刻。',
 'VOO：673.97，高718.47（10/6），D6.19%；15%/25%价610.70/538.85。距首档8.81个百分点，从现价需再跌9.39%。Yahoo与Barchart日期/收盘/高点一致；StockAnalysis673.90差0.07，阶段不受影响，按已交叉支持的统一日线推进至11/5。',
 'BRK.B：572.33，11/5盘中新高586.30，D2.38%；更新15%/25%价498.36/439.73。距首档12.62个百分点，从现价需再跌12.93%。Yahoo与MarketScreener同日OHLC表一致；StockAnalysis收571.97差0.36。高点上移带动观察价上移，仍非接近档；单一公司不能机械套ETF仓位。',
 'QQQM/VOO/BRK.B的15%/25%条件不扩展到其他监测证券。QQQ仍退役；没有自动交易。官方可比收盘未成功取得，本次为第三方交叉支持，并披露分歧；价格定义及修正原因尚不明确。'
 ],qq+[source('VOO Barchart历史','https://raymondjames.websol.barchart.com/?0=NEWS&1_selected=etfQuote&module=etfDetail&region=US&symbol=VOO'),source('BRK.B MarketScreener历史','https://www.marketscreener.com/quote/stock/BERKSHIRE-HATHAWAY-INC-11916/quotes/')] ))
prices=[]
for sym in ['NOW','CRM','GEHC','CGNX']:
 a=assets[sym];v=a['valuation'];m=metrics[sym];gap=(v['discount_price']/m['close']-1)*100
 prices.append(f"{sym}：11/5 Yahoo收盘{m['close']:.2f}美元、{m['day_pct']:+.2f}%；11/5专题基准{v['base_value']:.2f}、基准八折{v['discount_price']:.2f}，从现价到该条件价还需变动{gap:+.2f}%。估值参数没有因为新报价自动重写。")
delta=(69-56.5)/171.027
prices+=['第二来源同日收盘依次为NOW102.35、CRM222.35、GEHC83.76、CGNX47.50美元，与Yahoo相差0.01/0.06/0.01/0.01美元；不声称完全一致。四家均未达到现金流基准八折。GEHC盈利法基准90美元、八折72美元，与现金法68.68/54.94分开，不能平均后称便宜。',
 f'CGNX完整10-Q本次已取得，电话会已发生但本次未听原音；RealSense仍预计Q4交割并需分拆Facial Authentication业务。现金留任最高6900万美元高于昨日模型的目标5650万；若保守一次额外扣1250万、用1.71027亿稀释股，不计税和折现，基准价值减少约{delta:.3f}美元/股、八折价减少约{delta*.8:.3f}美元。仅作为上限敏感性，未偷偷替换基准，不影响当前无安全边际判断。']
brief['sections'].append(section('估值报价更新｜11/5下跌后，四股仍未到现金流折扣条件',prices,[cgnx]+[source(s+'历史报价',f'https://stockanalysis.com/stocks/{s.lower()}/history/') for s in ['NOW','CRM','GEHC','CGNX']]))
# Keep the full researched models, explicitly dated; retire obsolete daily-market sections.
for i in [0,1,2,3,4,5,9,10,11,12,13,14]:
 p=copy.deepcopy(old['sections'][i])
 if i<=4:
  p['title']='11/5估值专题留存｜'+p['title']
  p['paragraphs'].insert(0,'估值复核日11/5，详细模型中的报价基准为11/4；今天11/5收盘比较和新10-Q变化见上方“估值报价更新”，旧报价不作为新行情。')
 if i==4:
  p['title']='11/5估值专题留存｜CGNX现金流模型与RealSense资本桥'
  p['paragraphs'][-1]='11/6更新：完整Q3 10-Q已于11/5取得；电话会已发生，本次未听原音。现金留任上限与交割条件见最新更新，不能继续沿用“尚缺10-Q”的结论。'
  p['paragraphs'][-2]=p['paragraphs'][-2].replace('当前53.06','11/4基准价53.06').replace('下一步看电话会/完整10-Q、','下一步看电话会与10-Q细节、')
  p['sources'].append(cgnx)
 if i==5:
  p['paragraphs']=[('EPAM｜11/5 Q3已发布：收入14.2643亿美元、同比+2.3%，经营利润率12.3%；Q4增长指引−0.2%～+0.9%。管理层明确扩大FDE网络但未单列营收/利润。Q2约78%按工时材料收费是旧季度参照，不冒充最新Q3收费结构；新10-Q的收费结构仍待核。' if x.startswith('EPAM（') else x) for x in p['paragraphs']]
  p['sources'].append(epam)
 brief['sections'].append(p)
brief['sections'].append(section('Google与SOFI｜融资、信用及资本的新核验',[
 'Google：本次推进的是融资资本桥。债务本金增加60亿欧元，预计净现金59.7亿欧元，实际净到账与偿债未知；不直接拼进9/30美元资产负债表。固定票息核算为7.5亿×3.7%＋12.5亿×4.05%＋7.5亿×4.25%＋7.5亿×4.5%＋7.5亿×4.875%＋10亿×5.25%＝每年2.330625亿欧元，另有7.5亿浮息债。未做美元汇率或对冲假设；原模型中的融资成本、净债务与FCFF必须保持一致，避免重复扣息。',
 'GOOGL公司研究报价为11/5 Yahoo282.57美元，第二源282.60，差0.03；仅用其研究公司，不混用GOOG C类报价。10/30完整Q3模型及11/5的反向DCF仍是旧资本/经营假设下的条件敏感性，尚未完成融资后TPU营运资金重估，旧入场价继续暂停。',
 'SOFI新Q3 10-Q已发布并读取：10/15以现金偿还4.28亿美元到期可转债，此批未发普通股；不代表其他SBC/可转债没有稀释。9/30银行CET1估算14.9%，低于年末16.4%，公司披露仍满足要求。Q3总净核销率1.62%同比降28bp，但金额增至2.125亿美元；扩表使比率与金额方向可不同。',
 f"SOFI 11/5 Yahoo16.04美元、第二源16.03。沿已披露9/30每股有形净资产7.48，当前P/TBV代理{16.04/7.48:.2f}倍；未因下跌确认低估。10/15现金偿债与债务减少要成对考虑，不能只减少净资产；下一步核贷款公允价值/销售留存、存款成本、资本回报及真实股数。银行存款属于经营资金，不用工业企业净现金DCF。"
 ],google+[csource('sofi_10q','SoFi 11/5完整10-Q'),source('GOOGL报价','https://stockanalysis.com/stocks/googl/history/'),source('SOFI报价','https://stockanalysis.com/stocks/sofi/history/')]))
brief['sections'].append(section('SOXX拆股及行情缺口｜保留旧日期，拒绝错误收益',[
 '官方已核SOXX 3:1拆股，11/5开盘按新单位交易。Yahoo今日日线131.90美元，但11/2–11/4仍约450旧单位、10/30已约157新单位；直接拼接会制造−70.72%假日跌幅及错误均线。统一前不发布该序列，卡片保留11/4最后有效数据，450.41是拆股前旧单位，不是11/5报价。不能把整段再除3，避免已调整部分重复调整。',
 'XSW 11/5提供方开盘211.65高于当天最高209.00，OHLC内部矛盾；此次拒绝并保留11/4。其他41项已取得11/5完整日线，不能因两项失败声称全部43项最新或整个更新失败。',
 '新增行情校验会拒绝拆股量级断裂和不可能的OHLC；失败保留每项上次有效日期。MRNA 8/19历史极端跳涨仍影响长区间回报/波动，原事件因果尚缺；DRAM、SKHY、SPCX等短历史不补MA200/完整52周。曲线v2与1/2/3年联动口径保留。'
 ],[soxx,source('SOXX Yahoo历史','https://finance.yahoo.com/quote/SOXX/history/'),source('XSW Yahoo历史','https://finance.yahoo.com/quote/XSW/history/')]))
ext=read(DAY/'extended_quotes.json'); selected=[x for x in ext['observations'] if x['symbol'] in ['QQQM','VOO','BRK-B','GOOGL','SOFI']]
paragraphs=['本次分钟采集UTC11/5 23:29:50＝北京时间11/6 07:29:50，冬令时美东18:29:50。11/5盘后尚在进行，通常20:00 EST＝北京09:00结束；下一11/6盘前尚未开始，不展示昨日盘前冒充今天。以下为不同时间的参考价，非最终盘后收盘。']
for x in selected:
 p=x['post'];paragraphs.append(f"{x['symbol']}：11/5盘后{p['price_usd']:.2f}美元，{p['bar_start_et']}／北京{p['bar_start_beijing']}，相对同日Yahoo常规收盘{p['change_vs_reference_pct']:+.2f}%。该分钟柱成交量为0，可能是延续报价，不声称最新实际成交。")
paragraphs.append('第二源时刻不同：QQQM265.30（18:01 EST）、VOO670.35（18:16）、BRK.B569.50（18:12）、GOOGL278.90（18:24）、SOFI15.60（18:18）。与上列不同时间参考并列，不能称同刻一致；BRK.B另源18:30参考574.74与Yahoo方向也不同，时段数据未确认统一成交口径。常规提醒不采用盘后价格，整日收益也不把两个百分比相加。')
brief['sections'].append(section('盘后观察｜各自时刻与来源差异',paragraphs,qq+[source('VOO','https://stockanalysis.com/etf/voo/history/'),source('BRK.B','https://stockanalysis.com/stocks/brk.b/history/'),source('GOOGL','https://stockanalysis.com/stocks/googl/history/'),source('SOFI','https://stockanalysis.com/stocks/sofi/history/')]))
brief['sections'].append(section('宏观与下一周日历｜今晚非农，CPI为11/10',[
 '11/5正常常规交易，下一11/6 09:30–16:00 EST＝北京时间11/6 22:30至11/7 05:00。冬令时相差13小时。11/11不是NYSE股票休市日，债券与政府日历另核。',
 '11/5 VIX收28.18，前16.61，+11.57点/+69.66%，Cboe与Yahoo及第三方正文一致。财政部11/5日度2年4.46%、10年4.84%，较11/4分别−12bp/−6bp。收益率是约15:30 EST指示性买价拟合，非股票收盘成交；Cboe历史CSV/FRED仍落后一日，未拿旧值冒充新值。利率下降伴随波动率急升，不能只当估值利好。',
 '11/6：MRNA Q3电话会08:00 EST＝北京21:00；非农/就业08:30＝21:30。11/10：10月CPI08:30＝21:30，按BLS最新日程，不沿用11/12。均尚未公布。11/12周四初请预计08:30（依DOL周四规则、未列例外）；CSCO盘后业绩/16:30电话会及AMAT16:30电话会，均为北京11/13 05:30电话会。',
 '未来一周没有FOMC决议；10/28决议已发布，目标区间3.75%–4.00%未变。下一会议12/8–9，10月纪要11/18。NVDA业绩计划11/17，超出未来一周。预告不当已发生业绩；本次不猜宏观数值和市场预期。',
 'SGOV本周已新核官方30日SEC收益率3.83%，截至11/4，费率0.09%、有效久期0.11年。12个月派息收益率3.63%是另一口径，不能当未来总回报；基金持仓展示仍保留原披露日。'
 ],[bls,vix,source('NYSE交易时段','https://www.nyse.com/trade/hours-calendars'),source('美国财政部11月收益率','https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value=202611&type=daily_treasury_yield_curve'),source('FOMC会议表','https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'),source('MRNA官方日历','https://investors.modernatx.com/events-presentations'),source('SGOV官方','https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf'),source('Cisco官方预告','https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2026/m11/cisco-schedules-conference-call-for-q1-fiscal-year-2027-financial-results.html?source=rss'),source('AMAT官方活动','https://investor.appliedmaterials.com/events/event-details/q4-2026-applied-materials-earnings-conference-call')]))
brief['sections'].append(section('Reddit新增讨论｜事实、观点与反证分开',[
 '本次过去24小时窗口：r/investing New公开RSS成功取25条及绝对时间；其他五个优先社区RSS429、部分New/Top网页旧缓存，覆盖不完整。已打开下列原帖，未采用热度判断真假，不把访问失败写成没有新内容。',
 '已核旧项目事实/新增观点：1xox8vh，r/investing，北京11/6 07:09:55。申请MW、签约MW、通电MW需分开。Georgia Power 7/22、8/26旧披露含OpenAI 3.2GW、25年合同及成本承担安排；OpenAI项目分2028–2032推进，不是今天新订单。反证是已有获批合同，不能全盘否定infra；下一步核并网、融资与回款。本帖评论未取得，“41项中40项反对”未核不采纳。',
 '仅情绪/待核政策观点：1xomi9p（北京00:06:23）及1xovbku（05:47:11）合并讨论政策冲击或估值问题；已读评论有人关注云厂商资本开支，有人提醒收入不等于现金及反对事后政治叙事。下一步看实际法规、许可及公司订单；不把标题跌幅或发帖人动机当事实，不改变买入条件。',
 '已核基金范围/待核配置观点：1xows2i，r/investing，北京06:49:05。以VGT替代宽基的观点遇到行业集中反证；Vanguard截至9/30官方材料证实VGT同时涵盖软件、硬件与半导体。看好应用不等于应增全部IT敞口；下一步按真实持仓日拆分重叠，不冒称实时权重。'
 ],[source('MW讨论原帖','https://www.reddit.com/r/investing/comments/1xox8vh/ai_demand_can_boom_while_datacenter_stocks/'),source('政策/估值讨论','https://www.reddit.com/r/investing/comments/1xomi9p/nasdaq_down_6_coreweave_down_55_in_a_month_is_the/'),source('相关反方讨论','https://www.reddit.com/r/investing/comments/1xovbku/why_the_postmidterm_ai_selloff_is_a_massive/'),source('VGT原帖','https://www.reddit.com/r/investing/comments/1xows2i/the_argument_for_vgt_in_a_boglehead_portfolio/'),source('Georgia Power7月合同','https://www.georgiapower.com/news-hub/press-releases/georgia-power-to-serve-openai-project-in-effingham-county.html'),source('8月批准披露','https://www.georgiapower.com/news-hub/press-releases/contract-openai-approved-part-portfolio-delivering-950-million-annual-savings.html'),source('OpenAI项目计划','https://openai.com/index/building-ai-infrastructure-with-the-effingham-county-community/'),source('VGT官方季度资料','https://fund-docs.vanguard.com/F0958.pdf')]))
brief['sections'].append(section('FiNews读取范围与缺口',[
 '实际公开HTTP取得交易日11/5最新首页，页面更新23:14:30 UTC，采集23:27:48 UTC；读取热力图、8段摘要、日历、21条新闻摘要及行情/情绪表。网页工具缓存仍是11/4，本次没有将缓存冒充最新。',
 '科技/AI下跌与政策风险是聚合线索，Yahoo综述、CNBC政策及就业前瞻原文未取得，不将资金流和政策因果升级为已核事实；多条相同原文转述不算独立证据。CPI前瞻标签链接实际指向就业路径，未沿用错配。行情另取原始序列，事件时刻回查BLS。'
 ],[source('FiNews最新页','https://finews.fyi/'),bls]))
market=DAY/'market_sections.json'
if market.exists():brief['sections'].extend(read(market))
# Public card corrections only; no portfolio data is read into this artifact.
assets['SOXX']['facts']['notes']=[x for x in assets['SOXX']['facts']['notes'] if '拆股' not in x]+['官方已核2026-11-05起3:1拆股。当前提供方部分历史单位混杂，今日指标暂不发布；保留11/4拆股前旧单位，非今日报价。']
assets['SOXX']['facts']['sources'].append({**soxx,'asof':'2026-10-23公告，2026-11-05生效'})
assets['SOXX']['next']='等待提供方统一3:1拆股历史；不可把机械价格下降或混合序列−70%当投资亏损。'
assets['XSW']['next']='11/5 OHLC矛盾，保留11/4最后有效值；等待正确完整日线，不拼造数据。'
assets['GOOGL']['facts']['fact_lines']+=['11/5完成60亿欧元优先债发行；预计净额59.7亿欧元，实际到账及偿债未核。']
assets['GOOGL']['facts']['sources'] += [{**s,'asof':'2026-11-04/05'} for s in google]
assets['GOOGL']['next']='融资已完成；核实际净额/偿债、TPU库存应收与现金回收，完整资本桥重估前旧研究买价继续暂停。'
assets['SOFI']['facts']['fact_lines']=[x for x in assets['SOFI']['facts']['fact_lines'] if 'P/TBV' not in x]+['9/30有形每股净资产7.48美元；11/5收盘16.04对应P/TBV约2.14倍，非低估结论。','11/5完整10-Q：10/15现金偿还4.28亿美元可转债；9/30银行CET1估算14.9%，Q3总净核销率1.62%与核销额2.125亿美元并列看。']
assets['SOFI']['facts']['sources'].append({**csource('sofi_10q','SoFi完整Q3 10-Q'),'asof':'2026-11-05申报，财务截至9/30'})
assets['SOFI']['next']='完整10-Q已取得；核贷款销售/留存、公允价值假设、存款成本、监管资本与真实股数，估值用银行口径。'
assets['EPAM']['facts']['fact_lines']=['2026Q3收入14.2643亿美元，同比+2.3%、有机恒汇率+2.5%；GAAP经营利润率12.3%，EPS2.53，调整EPS3.51。','Q4收入增长指引−0.2%至+0.9%；前三季经营现金流2.501亿美元，去年同期3.720亿。','明确扩大FDE网络，未单列FDE收入/利润；预计11/9当周的5亿美元ASR尚为计划。']
assets['EPAM']['facts']['sources']=[{**epam,'asof':'2026-11-05'}]
assets['EPAM']['facts']['gaps']=['最新收费结构、FDE单列营收/利润及正常化估值待核；AI交付不自动等于软件经济性。']
assets['EPAM']['facts']['reviewed_date']='2026-11-06'
assets['EPAM']['next']='核FDE收入兑现、每员工收入、回款与固定价利润；Q3已公布，估值仍待完成。'
assets['CGNX']['facts']['sources'].append({**cgnx,'asof':'2026-11-05申报，季度截至10/4'})
assets['CGNX']['facts']['gaps']=['完整Q3 10-Q已取得，电话会原音未听；RealSense独立利润、交割与激励实际结算仍缺。']
assets['CGNX']['facts']['notes'].append(f'11/6补核现金留任最高6900万美元；较5650万目标多1250万，按原股数未折现影响约−{delta:.3f}美元/股，未改基准。')
assets['CGNX']['next']='10-Q已取得；核RealSense分拆前提与交割、留任上限及目标利润，不能因今日下跌认定便宜。'
assets['CGNX']['valuation']['next']=assets['CGNX']['next']
assets['SGOV']['facts']['notes']=[x for x in assets['SGOV']['facts']['notes'] if not x.startswith('30日SEC')]+['30日SEC收益率3.83%，截至2026-11-04，本次11/6重新核验；非派息率或未来总回报。']
assets['SGOV']['facts']['sources'].append({'title':'SGOV官方SEC收益率本周复核','url':'https://www.ishares.com/us/products/314116/ishares-0-3-month-treasury-bond-etf','asof':'SEC收益率2026-11-04，其他字段各自日期'})
write(SITE/'worker/daily-brief.json',brief);write(DAY/'daily-brief.json',brief);write(SITE/'worker/seed.json',seed)
write(DAY/'valuation_update.json',{'reviewed_at':now,'basis_date':'2026-11-05 models','market_session':'2026-11-05','comparison':prices,'cgnx_max_retention_delta_per_share':delta,'google_financing':{'currency':'EUR','new_debt_principal':6000000000,'estimated_net_proceeds':5970000000,'estimated_net_cash_less_principal':-30000000,'fixed_coupon_annual':233062500,'floating_principal':750000000,'actual_cash_receipt_verified':False,'fx_conversion_used':False}})
print('brief',brief['report_date'],len(brief['sections']),'sections; public cards updated')
