from pathlib import Path
import json, datetime, html, re
root=Path(__file__).parent
review=datetime.datetime.now(datetime.timezone.utc).isoformat()
urls={
'IGV':'https://www.ishares.com/us/products/239771/ishares-north-american-techsoftware-etf',
'XSW':'https://www.ssga.com/us/en/individual/etfs/state-street-spdr-sp-software-services-etf-xsw',
'IHI':'https://www.ishares.com/us/products/239516/ishares-us-medical-devices-etf',
'BOTZ':'https://www.globalxetfs.com/funds/botz',
'AIQ':'https://www.globalxetfs.com/funds/aiq'}
# Scenario inputs are research assumptions, not issuer guidance or historical valuation norms.
inputs={
'IGV':dict(anchor=102.23,pe=33.05,fee=.0038,base=(.12,28),stress=(0,22),bull=(.15,33.05),holdings=[('MSFT',8.91),('PLTR',8.55),('PANW',8.39),('CRWD',7.92),('ORCL',7.59)],count=105,
 pe_basis='发行人PE采用各成分最近财政年度EPS，并排除负PE；未披露被排除权重，不能称TTM或全组合GAAP盈利。',
 facts='11/11前五MSFT/PLTR/PANW/CRWD/ORCL合计41.36%；应用软件50.41%、系统软件43.40%。费率0.38%。偏软件大公司，仍含云基础设施、安全和传统软件。',
 rationale='基准假设盈利分母代理年增12%、终值28倍，主动测试软件高倍数压缩；AI收费增长仍可能被席位减少、推理成本和SBC抵消。',
 next='观察头部持仓AI增量收费、SBC后每股现金流和传统席位流失；重构含亏损公司权重的组合盈利，若利润不增则不能只因跌价认定便宜。'),
'XSW':dict(anchor=208.41,pe=18.93,fee=.0035,base=(.10,18),stress=(-.03,14),bull=(.15,20),holdings=[('BRZE',1.41),('GDYN',1.27),('VIA',1.19),('APPN',1.13),('NETSKOPE',1.12)],count=129,
 pe_basis='基金FY1 PE18.93为预期下一年EPS的加权调和口径，包含正负极端值；指数另列PE26.87，不能当同一分母。',
 facts='11/11应用软件67.37%、系统软件21.36%、IT咨询9.10%；修正等权，头五合计6.12%，费率0.35%。FactSet平均3–5年EPS增速预测18.14%，不是已实现或基金承诺。',
 rationale='基准把分母代理增速压至10%、终值18倍，低于披露的预测均值；分散降低单一龙头集中，但中小软件及服务企业面临模型替代和融资风险。',
 next='核盈利预测下修、亏损持仓权重与订单现金转化；用同一FY1调和算法追踪估值，不直接与IGV剔负PE排名。'),
'IHI':dict(anchor=58.17,pe=33.60,fee=.0037,base=(.08,28),stress=(0,22),bull=(.12,33.60),holdings=[('ABT',17.38),('ISRG',14.60),('MDT',11.43),('IDXX',5.45),('EW',4.90)],count=49,
 pe_basis='发行人PE采用各成分最近财政年度EPS并排除负PE；不是可直接比较的全组合TTM PE。',
 facts='11/11 ABT/ISRG/MDT合计43.41%，GEHC4.62%；费率0.37%。医疗器械组合，含诊断、植入物和手术设备，AI收入未单列，不能当纯医疗AI。',
 rationale='基准分母代理年增8%、终值28倍，给医疗器械增长而不假设AI单独爆发；手术量和耗材复购是支撑，支付压价、产品召回和关税是反证。',
 next='核ABT/ISRG/MDT手术与设备需求、定价及毛利；AI商业化需证明付费，不把临床部署等同新增收入。'),
'BOTZ':dict(anchor=32.23,pe=30.12,fee=.0068,base=(.08,25),stress=(-.03,20),bull=(.12,30.12),holdings=[('ISRG',10.38),('FANUC',8.45),('KEYENCE',8.30),('ABB',7.66),('NVDA',6.65)],count=81,
 pe_basis='Global X展示AltaVista 2026年份PE30.12（2025栏42.97）；页面未完整说明预期/实现混合、负盈利和聚合算法，不能称GAAP TTM。',
 facts='11/11前五合计41.44%，费率0.68%；10/31工业46.21%、IT32.52%，中国14.42%、香港2.43%。机器人硬件与自动化主导，非纯软件落地，含境外和汇率敞口。',
 rationale='基准分母代理年增8%、终值25倍，计入工业资本开支周期和估值压缩；机器人需求不等于各设备商都能维持利润。',
 next='核订单增长是否转交付与现金，持续追踪中国/香港暴露及汇率；补AltaVista负盈利处理和预测覆盖后才讨论更精确穿透价值。'),
'AIQ':dict(anchor=59.91,pe=18.49,fee=.0068,base=(.10,18),stress=(-.03,14),bull=(.15,20),holdings=[('PLTR',4.10),('MSFT',4.01),('TSLA',3.59),('SPCX',3.47),('AMZN',3.34)],count=88,
 pe_basis='Global X展示AltaVista 2026年份PE18.49（2025栏27.74）；未完整核定会计口径、负盈利处理与预测覆盖，不可据此直接认定低估。',
 facts='11/11前五合计18.51%，费率0.68%；10/31软件服务36.00%、半导体22.64%、硬件13.92%、中国5.58%。应用与基础设施混合，和科技/芯片ETF存在经济敞口重叠。',
 rationale='基准分母代理年增10%、终值18倍，不依赖估值扩张；较低表面PE也可能受周期利润、预测口径与芯片权重影响。',
 next='分拆软件付费、芯片周期及大型平台利润，核2026预测修订；补AltaVista口径前，不因18.49倍低于IGV就判断更便宜。')}
method={
 'name':'三年组合盈利代理/倍数敏感性；不是穿透DCF、公允NAV或发行人目标价',
 'anchor_date':'2026-11-11','market_session':'2026-11-12','horizon_years':3,'required_return_assumption':.10,
 'formula':'scenario_present_reference = anchor_price * (1+growth)^3 * (exit_multiple / disclosed_PE) * (1-expense_ratio)^3 / (1+required_return)^3',
 'reverse_formula':'required_growth = (current_close / anchor_price)^(1/3) * (1+required_return) * (disclosed_PE / exit_multiple)^(1/3) / (1-expense_ratio) - 1',
 'limitations':[
 'ETF份额没有等同经营公司的每股利润。anchor_price/disclosed_PE只是映射单位，不是可审计ETF EPS；尤其剔除亏损公司的PE不能还原整个基金利润。',
 '起点市场价与公开倍数统一用11/11；11/12 Yahoo常规收盘仅作今日比较，未把11/11组合估值冒称11/12新披露。',
 '所有未来盈利增长、退出倍数、10%要求收益和八折缓冲均为研究假设，不是预测、历史估值均值或已批准的交易规则。',
 '增长按各基金当前披露分母的同口径滚动代理理解。XSW为FY1预期口径，终点也采用未来当时FY1口径，不混为TTM。Global X年份口径未充分核清，情景可信度更低。',
 '仅作价格回报敏感性，未加分红、税费与买卖价差；未来三年基金费用每年扣一次，未重复扣起点价历史费用。含分红总回报通常不同。',
 '成分调仓、净亏损权重变化、估值算法改变和汇率都会破坏恒定组合假设。当前合理研究结论可以是无充分安全边际，而不是强造精确价值。',
 '基准八折只是模型缓冲，不等于最大回撤20%，也不替代用户既定15%/25%观察规则；压力场景不是最坏情况。'
 ]}
outputs={}; model={'reviewed_at':review,'methodology':method,'funds':{}}
for s,d in inputs.items():
 meta=json.loads((root/'raw'/f'{s}.json').read_text())['chart']['result'][0]['meta']
 close=float(meta['regularMarketPrice'])
 quote_time=datetime.datetime.fromtimestamp(meta['regularMarketTime'],datetime.timezone.utc).isoformat()
 assert quote_time.startswith('2026-11-12T21:00:'),(s,quote_time)
 scenarios={}
 for name in ('stress','base','bull'):
  g,m=d[name]
  terminal=d['anchor']*(1+g)**3*m/d['pe']*(1-d['fee'])**3
  pv=terminal/(1.10**3)
  scenarios[name]={'growth_assumption':g,'exit_PE_assumption':m,'terminal_price_sensitivity':round(terminal,4),'present_reference':round(pv,4),'three_year_price_return_from_latest_close_pct':round((terminal/close-1)*100,4)}
 base=round(scenarios['base']['present_reference'],2);stress=round(scenarios['stress']['present_reference'],2);bull=round(scenarios['bull']['present_reference'],2);discount=round(scenarios['base']['present_reference']*.8,2)
 req=((close/d['anchor'])**(1/3)*1.1*(d['pe']/d['base'][1])**(1/3)/(1-d['fee'])-1)*100
 sources=[{'title':s+' 发行人产品页：估值/费率/实际披露日期','url':urls[s]}]
 if s in ('IGV','IHI'):
  slug='ishares-expanded-tech-software-sector-etf' if s=='IGV' else 'ishares-u-s-medical-devices-etf'
  prod='239771' if s=='IGV' else '239516'
  sources.append({'title':s+' 官方持仓CSV，2026-11-11','url':f'https://www.ishares.com/us/products/{prod}/{slug}/latest-holdings.csv'})
 sources.append({'title':s+' 11/12常规收盘（Yahoo，单源参照）','url':f'https://finance.yahoo.com/quote/{s}/history/'})
 basis=(f'11/12常规收盘${close:.2f}（Yahoo单源）；11/11同日价${d["anchor"]:.2f}、PE{d["pe"]:.2f}作模型起点。'+d['pe_basis']+d['facts']+d['rationale']+
 f'三年、要求收益10%、扣年度费率的价格情景现值：压力${stress:.2f}／基准${base:.2f}／乐观${bull:.2f}；基准八折${discount:.2f}。这是条件映射，不是基金内在价值；不含分红。按基准终值倍数，现价需约{req:.1f}%的年化分母代理增长才能达到模型10%年化价格回报。倍数、增长与八折均为研究假设。')
 outputs[s]={'judgment':'情景估值已完成：当前高于基准参考，尚无充分安全边际','basis':basis,'next':d['next'],'reviewed_at':review,'market_session':'2026-11-12','valuation_type':'conditional_fund_sensitivity','base_value':base,'stress_value':stress,'bull_value':bull,'discount_price':discount,'sources':sources}
 if s=='AIQ':outputs[s]['judgment']='情景估值已完成：接近基准参考，但缺乏八折缓冲；低表面PE未证明低估'
 model['funds'][s]={'price_reference':{'official_anchor':d['anchor'],'official_anchor_date':'2026-11-11','latest_close':close,'latest_close_time_utc':quote_time,'latest_close_source':'Yahoo; 本次单源参照'},'disclosed_PE':d['pe'],'disclosed_PE_date':'2026-11-11','PE_basis':d['pe_basis'],'expense_ratio':d['fee'],'holdings_date':'2026-11-11','holding_count':d['count'],'top_five_weights':d['holdings'],'base_assumption_rationale':d['rationale'],'scenarios':scenarios,'required_growth_at_current_price_pct':round(req,4),'sources':sources}
(root/'valuation_funds.json').write_text(json.dumps(outputs,ensure_ascii=False,indent=2)+'\n')
(root/'valuation_funds_model.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n')
lines=['# 五只应用相关ETF估值复核｜2026-11-13','',f'复核时间：{review}。最新比较价为11/12美国常规收盘（美元、Yahoo单源），官方估值与持仓最新可读日11/11；不能混为同日披露。','', '这次完成的是有明示假设、可复算的基金组合情景估值。五只均未显示足够的基准八折缓冲；不以行业标签、股价回撤或较低跨供应商PE直接认定低估。','', '## 统一方法','',method['formula'],'']
lines += ['- '+x for x in method['limitations']]
lines += ['', '|基金|11/12收盘|11/11公开PE|年费率|压力现值|基准现值|乐观现值|基准八折|', '|---|---:|---:|---:|---:|---:|---:|---:|']
for s,d in inputs.items():
 o=outputs[s]; p=model['funds'][s]['price_reference']['latest_close']
 lines.append(f'|{s}|${p:.2f}|{d["pe"]:.2f}|{d["fee"]*100:.2f}%|${o["stress_value"]:.2f}|${o["base_value"]:.2f}|${o["bull_value"]:.2f}|${o["discount_price"]:.2f}|')
for s,o in outputs.items():
 lines+=['',f'## {s}', '', o['judgment'], '',o['basis'],'','下一核查：'+o['next'],'']+['- ['+x['title']+']('+x['url']+')' for x in o['sources']]
lines+=['','## 采集边界','','iShares产品HTML与两份持仓CSV、SSGA产品HTML已保留于valuation_funds_raw；Global X官方页面通过web工具成功读取，随后为落原始HTML的两次curl请求均返回429，已停止直接重试。Global X摘录事实在模型中保留，不能声称其HTML已下载成功。官方PE未作另一独立基本面数据库交叉确认，财务口径不齐已显式降级。']
(root/'valuation_funds_model.md').write_text('\n'.join(lines)+'\n')
# Preserve a short locally-read definition without claiming a complete independently derived denominator.
for s in ['IGV','IHI']:
 t=html.unescape(html.unescape((root/'valuation_funds_raw'/f'{s}_product.html').read_text()))
 start=t.find('Each holding\'s P/E')
 (root/'valuation_funds_raw'/f'{s}_PE_definition.txt').write_text(t[start:start+350]+'\n')
print(json.dumps({s:{'base':o['base_value'],'stress':o['stress_value'],'bull':o['bull_value'],'discount':o['discount_price']} for s,o in outputs.items()},indent=2))
