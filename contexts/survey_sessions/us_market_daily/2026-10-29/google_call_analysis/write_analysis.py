from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
p=Path(__file__).resolve().parent
sources=[
 {'id':'official_release','url':'https://www.sec.gov/Archives/edgar/data/1652044/000165204426000080/googexhibit991q32026.htm','kind':'primary_SEC_earnings_release','read_scope':'financial tables, webcast provenance','status':'web_body_read'},
 {'id':'official_replay','url':'https://www.youtube.com/watch?v=X9mmCagxJTo','kind':'official_call_replay','read_scope':'link confirmed from original SEC release; title only','status':'audio_not_played_captions_not_obtained'},
 {'id':'official_ceo','url':'https://blog.google/company-news/inside-google/message-ceo/alphabet-earnings-q3-2026/','kind':'primary_edited_CEO_remarks','read_scope':'CEO prepared remarks; not CFO or full Q&A','status':'web_body_read_and_public_html_archived'},
 {'id':'stockanalysis','url':'https://stockanalysis.com/stocks/googl/transcripts/712854-q3-2026/','kind':'Quartr_third_party_call_transcription','read_scope':'prepared CEO/CBO/Cloud/CFO remarks and Q&A','status':'web_body_read_CLI_archive_failed'},
 {'id':'benzinga','url':'https://www.benzinga.com/news/26/10/62679903/alphabet-q3-2026-earnings-call-transcript','kind':'third_party_corrected_call_transcription','read_scope':'CFO outlook, Search monetization, Cloud capacity and capital commitments; editor correction','status':'web_body_read_CLI_archive_failed'},
 {'id':'marketbeat','url':'https://www.marketbeat.com/earnings/reports/2026-10-28-alphabet-inc-stock/','kind':'third_party_timestamped_call_transcription','read_scope':'48:49–49:41 TPU working capital; 53:55 committed contracts and product margin gap','status':'web_body_read'},
 {'id':'fool','url':'https://www.fool.com/earnings/call-transcripts/2026/10/29/alphabet-googl-q3-2026-earnings-call-transcript/','kind':'third_party_call_transcription','read_scope':'CFO remarks and Q&A cross-read; summary EPS label not used','status':'web_body_read_CLI_archive_failed'}
]
facts={'call_us':'2026-10-28T16:30:00-04:00','call_beijing':'2026-10-29T04:30:00+08:00','units':'USD billions unless stated','q3_ocf':42.290,'q3_cash_capex':51.355,'q3_fcf':42.290-51.355,'ec_fine_cash_payment':5.2,'fine_only_cash_adjustment':42.290-51.355+5.2,'fine_adjustment_status':'own arithmetic, not company adjusted FCF or sustainable run rate','cloud_revenue':30.709,'cloud_operating_income':11.121,'cloud_segment_margin_pct':11.121/30.709*100,'capex_2026_guidance':[195,205],'capex_2026_change_this_call':'unchanged','capex_2027':'significantly higher; no exact range provided','q3_tpu_inventory_cash_impact':'not separately quantified','tpu_product_margin':'not separately disclosed','cloud_growth_ex_tpu_pct':'not quantified','quote_policy':'No current price used; this is a call analysis, not a live market snapshot','model_policy':'Old Google entry bands remain suspended; 217.36 partial sensitivity is not a full updated fair value; review working-capital intensity as well as capital bridge'}
claims=[
 {'topic':'Search','source_ids':['official_ceo','stockanalysis'],'fact':'query growth strongest in five years; management acknowledges lower AI Mode monetization; FX largest sequential deceleration driver','inference':'franchise resilience supported, incremental AI profitability not established'},
 {'topic':'Cloud','source_ids':['official_release','benzinga'],'fact':'103% revenue growth includes meaningful TPU sales; Q3 segment margin 36.2%; external bridging compute ramps Q4','inference':'do not extrapolate combined growth as recurring cloud growth or constant margins'},
 {'topic':'Cash','source_ids':['official_release','stockanalysis','marketbeat'],'fact':'negative 9.065B FCF includes 5.2B fine cash payment and TPU inventory build; contracts precede inventory','inference':'separate one-off payment and working capital from capex; no double counting or nine-month inventory addback'},
 {'topic':'Capital','source_ids':['benzinga'],'fact':'2026 capex unchanged, 2027 significantly higher','inference':'3–5-year per-share cash returns depend on reinvestment intensity, recovery and financing'}
]
(p/'call_sources.json').write_text(json.dumps({'checked_at_utc':datetime.now(timezone.utc).isoformat(),'sources':sources,'claim_checks':claims,'limits':['Full official audio not played; CFO/Q&A read through third-party transcriptions','Multiple transcripts are representations of the same call, not independent evidence of outcomes','No complete Q3 capital bridge rebuilt this turn','No current quote or new precise entry price asserted']},ensure_ascii=False,indent=2)+'\n')
(p/'analysis_checks.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n')
report='''# Google三季报电话会分析｜2026-10-29

**结论：Google的AI需求和搜索入口仍有竞争力，但这次电话会尚不足以证明股票低估。** 对你“3–5年、尽量控制回撤”的目标，我会继续重点研究，暂缓大额首笔；先核算每股现金回报，再讨论新入场价。

最新为**2026年第三季度电话会**，美东10月28日16:30／北京时间10月29日04:30。[官方回放](https://www.youtube.com/watch?v=X9mmCagxJTo)由[SEC原始财报](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000080/googexhibit991q32026.htm)直接链接。以下读了官方CEO稿及第三方完整转录的CFO发言、分析师问答；未播放完整原音，转录差异仍需留意。这是电话会专题，不是实时行情更新。

**今天对你最重要的事**

| 电话会增量 | 对投资判断的影响 | 当前判断 |
|---|---|---|
| AI搜索使用增加，但AI Mode变现仍较低 | 使用量与利润增长需要分别验证 | 搜索护城河仍在，商业化过渡有成本 |
| 云增长包含TPU系统销售，外购算力成本将更多进入Q4 | 不能直接外推103%增长与36.2%利润率 | 需求强，盈利质量仍需拆分 |
| 负现金流含罚款与备货；2027资本开支仍会上升 | 既要避免过度悲观，也不能轻率加回全部支出 | 改现金流模型，暂不恢复旧买入价 |

**1．搜索：最重要的是AI查询能赚多少钱**

官方CEO稿强调，搜索查询同比增速为五年来最高。说明Google仍能吸引用户，AI也能创造新搜索需求；但这是管理层披露的使用指标，不能直接当作新增利润。[Google官方CEO发言](https://blog.google/company-news/inside-google/message-ceo/alphabet-earnings-q3-2026/)

问答中，商业负责人承认AI Mode变现较低，增加的相关查询影响了搜索增长表现；同时解释，较上季增速放缓的最大因素是汇率，另有广告行业与世界杯基数因素。广告正在向更多市场和多轮交互扩展。[电话会问答转录](https://stockanalysis.com/stocks/googl/transcripts/712854-q3-2026/)

**我的分析：** “AI会立即摧毁Google搜索”缺少这次业绩支持；“AI流量上涨必然增加利润”同样没有被证明。你应关注AI商业查询的变现效率、广告转化与推理成本能否一起改善。反证是使用量继续上升，但搜索收入和利润持续跟不上。

**2．云：103%的增长，要拆成服务与系统销售**

原始财报显示云收入307.09亿美元，同比增长约103%；云分部营业利润111.21亿美元，利润率约36.2%。TPU系统销售是增长的重要组成部分。[SEC财报与分部表](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000080/googexhibit991q32026.htm)

CFO说明，外部补充算力到Q3末才上线，对当季利润率影响有限；Q4使用增加，近期利润率会有压力。未披露剔除TPU系统销售后的精确增速，也未单列TPU毛利率。[CFO发言与问答](https://www.benzinga.com/news/26/10/62679903/alphabet-q3-2026-earnings-call-transcript)

**我的分析：** 软件服务与硬件系统的回款周期、利润和估值倍数不同。不能把合计增长全部视为可重复的云服务增长，也不能默认本季利润率长期保持。下一项关键证据是外部算力成本进入后，服务增长和实际利润能否仍支持投入回报。

**3．现金流：需要修正此前过于单一的解释**

Q3经营现金流422.90亿美元，现金资本开支513.55亿美元，相减得到自由现金流**−90.65亿美元**。CFO解释，现金流还受52亿美元欧盟罚款付款和TPU备货影响。[现金流原表](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000080/googexhibit991q32026.htm) · [CFO转录](https://stockanalysis.com/stocks/googl/transcripts/712854-q3-2026/)

仅作单项算术调整，假设加回这笔52亿美元罚款付款，现金缺口仍为**−38.65亿美元**。这不是公司公布的调整后自由现金流，也不是可持续水平；没有加回无法单独量化的Q3备货占款。

48:49–49:41的回答解释，TPU业务是先签合同、采购备货，再交付和回款；53:55附近管理层说相关库存对应已签合同。这属于营运资金周转，不能再作为自用基础设施资本开支重复扣除。[带时间的问答稿](https://www.marketbeat.com/earnings/reports/2026-10-28-alphabet-inc-stock/)

**我的分析：** 不能把全部负现金流都外推成永久恶化；但已签合同也不能保证毛利和及时回款。我的旧模型仅按新增收入的2%估计营运资金，随着TPU系统销售扩张，这个假设需要重新检验。不能简单把库存全加回，更不能把九个月库存变化当成单季现金影响。

**4．资本开支：2027年兑现压力仍在**

本次**维持**2026年1950–2050亿美元资本开支展望，并非本次新上调；2027年预计显著增加，详细指引留待Q4电话会。更高折旧、能源与运营成本会持续影响利润表。[CFO展望](https://www.benzinga.com/news/26/10/62679903/alphabet-q3-2026-earnings-call-transcript)

**我的分析：** 管理层相信投资回报会超过资本成本，这是展望，不能当作已兑现证据。你的持有窗口只有3–5年，不能完全依赖更远期现金流支撑价格。需要同时测算收入增长、设备更新、现金转化和融资稀释；资本开支高不自动等于浪费，需求强也不自动等于高回报。

**对你当前状态的建议**

**Google：保留优先研究，暂缓大额首次建仓。** 这场电话会提高了对需求的信心，也增加了对现金周转和成本结构的理解，但尚未补齐估值安全边际。

| 下一项核查 | 更支持入场研究的证据 | 会使我更谨慎的反证 |
|---|---|---|
| AI搜索变现 | 商业化改善能覆盖推理成本 | 流量增长，收入或利润持续落后 |
| 云服务与TPU分别评估 | 服务增长、产品经济性和外部算力后利润可解释 | 用硬件放量掩盖服务放缓或利润下降 |
| TPU交付与回款 | 库存转现金，合同兑现且毛利合理 | 备货、应收、回款周期连续恶化 |
| 资本桥与现金情景 | 新债、投资资产、租赁和稀释纳入后仍有安全边际 | 现金投入长期高于预期，依赖融资弥补 |

旧Google入场价继续暂停。此前约217美元的数字只是在保留六月资本桥时更新部分经营变量的敏感性，**不是本次完整重估的合理价**。本次不发布新的精确买入区间。

QQQM的按时间分批研究可单独推进，不必完全等待Google个股问题解决；单独增加Google仍会叠加ETF内已有暴露，个股应从股票总预算内安排。你尚未确认预算或持仓，不据此写成已执行配置。

**与AI半导体、机器人观察池的关系**

这是我的产业推断：高算力投入可继续支持定制芯片、网络互连、存储、电力和散热方向的需求研究，但还需要各供应商自己的订单、利润及估值证据。不能从Google投入增加就认定观察池股票低估，也不能把世界模型和机器人训练能力直接当成RRX、CGNX或ATS的订单。

**口径、核验和缺口**

- CEO官方编辑稿不覆盖完整CFO与问答；完整问答本次来自第三方转录，多份转录仍是同一场电话会。没有声称已听完原音。
- 本次未完成Q3完整资本桥、TPU独立利润与营运资金重估，没有重新抓取或混入实时盘前价格。
- 转录中的多年采购承诺须核对期限、重叠和弹性，不能全当当前债务、今年开支或直接从股权价值一次扣除。现金和有价证券也不能全当无风险现金。
- Benzinga已更正合作方名称为Crux AI；不采用旧稿的CoreWeave名称。Motley Fool摘要把2.12美元EPS标成Non-GAAP，本报告采用原始财报的GAAP口径，避免照搬聚合摘要。
- 网页工具读取了转录正文，但CLI保存三家转录失败；仅官方CEO网页成功存档。失败不写成未读，也不声称完整原文已离线保存。[读取范围与逐项核验](./call_sources.json) · [现金流算术与未决口径](./analysis_checks.json) · [存档状态](./archive_manifest.json)
'''
(p/'report.md').write_text(report)
print('Wrote report.md, call_sources.json, analysis_checks.json')
