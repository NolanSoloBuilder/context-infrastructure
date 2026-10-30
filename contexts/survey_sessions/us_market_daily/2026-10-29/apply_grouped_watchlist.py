from pathlib import Path
from datetime import datetime,timezone
import json,sys,re,hashlib
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parents[3]/'adhoc_jobs/us_market_daily'))
# Resolve reusable generator from workspace, independent of current shell cwd.
root=P.parents[3]
from render_watchlist import build
from collect import OBSERVATION_SYMBOLS
notes={
 'VOO':{'status':'准备首笔研究','next':'PCE与财报后完整交易日复核'},
 'QQQM':{'status':'准备首笔研究','next':'复核科技盈利、广度与利率'},
 'QQQ':{'status':'同指数对照','next':'与QQQM合并评估，避免重复配置'},
 'RRX':{'status':'安全边际不足','next':'11/3核现金转化、盈利调整与去杠杆'},
 'CGNX':{'status':'待价研究','next':'11/4业绩、RealSense整合成本'},
 'ATS':{'status':'高风险候选','next':'订单、回款和负债改善'},
 'GOOGL':{'status':'暂缓','next':'Q3完整资本桥重估，旧价位暂停'},
 'NVDA':{'status':'估值待完成','next':'核盈利分母、客户融资与现金回报'},
 'SMH':{'status':'行业比较','next':'半导体盈利周期、估值与行业广度'},
 'SOFI':{'status':'估值待完成','next':'信用损失、贷款出售风险与监管资本'},
 'BRK-B':{'status':'继续研究','next':'经营利润、保险赔付与投资披露'},
 'SGOV':{'status':'现金暂存候选','next':'SEC收益率、派息与流动性'}
}
(P/'watchlist_research.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')
# Add the two explicitly dated new public after-hours observations without changing existing evidence.
ev=json.load(open(P/'extended_verification.json'))
if not (P/'extended_verification_before_grouping.json').exists():(P/'extended_verification_before_grouping.json').write_bytes((P/'extended_verification.json').read_bytes())
for sym,price,t in [('CGNX',58.00,'19:53'),('NVDA',213.98,'19:59')]:
 m=next(r for r in json.load(open(P/'metrics.json')) if r['symbol']==sym)
 base=m['close'];row={'symbol':sym,'regular_close_usd':base,'afterhours_display_usd':price,'afterhours_change_vs_same_regular_pct':(price/base-1)*100,'display_quote_time_et':f'2026-10-28T{t}:00-04:00','display_quote_time_beijing':f'2026-10-29T07:{t[-2:]}:00+08:00','source_url':f'https://stockanalysis.com/stocks/{sym.lower()}/history/','verification_note':'Dated Stock Analysis after-hours snapshot; Yahoo times and prices differ, both retained in raw latest extended snapshot'}
 ev['rows']=[r for r in ev['rows'] if r['symbol']!=sym]+[row]
ev['grouping_update_at_utc']=datetime.now(timezone.utc).isoformat()
(P/'extended_verification.json').write_text(json.dumps(ev,ensure_ascii=False,indent=2)+'\n')
build(P,'2026-10-29','2026-10-29','not_started')
source=P/'report.md';before=P/'report_before_grouping.md'
if not before.exists():before.write_bytes(source.read_bytes())
s=before.read_text();pieces=re.split(r'^\*\*([^\n]+)\*\*\s*$',s,flags=re.M);intro=pieces[0];book={pieces[i]:pieces[i+1] for i in range(1,len(pieces),2)}
intro=intro.replace('本更新版已加入财报后的盘后反应、明确盘前状态，并新增SOFI固定研究观察','本更新版将全部观察标的按类别统一到一张总表，收盘、盘前、盘后及研究状态放在同一行')
sofi=book['SOFI研究观察'];sofi='\n'.join(line for line in sofi.splitlines() if not line.startswith('|'))
sofi=re.sub(r'该行全部美元[^\n]*','SOFI报价、回撤与盘后时点统一见分类观察总表；财报与估值细节仍见[SOFI研究来源](./sofi_sources.json)。',sofi)
book['SOFI研究观察']=sofi
book['机器人供应链筛选']=book['机器人供应链筛选'].replace('今天深入RRX，CGNX、ATS继续作为有条件研究候选，未把昨日价格冒充今日行情；也没有因为机器人题材认定整个行业低估。','今天深入RRX，CGNX、ATS继续作为有条件研究候选；本次已补齐三者10/28常规行情，统一列入机器人分组，未因题材认定整个行业低估。')
book['机器人供应链筛选']=book['机器人供应链筛选'].replace('RRX报价只有Stock Analysis明确标注常规收盘；另一报价接口虽同价但时点/涨跌分母不同，未认作独立收盘核验通过。本次不以它触发价格提醒。','本次新取Yahoo日线，与Stock Analysis明确日期的RRX、CGNX、ATS收盘相符；盘后数据有单源或时点差异，逐项保留在总表来源中。三者不加入原四标的提醒合同。')
metrics={r['symbol']:r for r in json.load(open(P/'metrics.json'))}
head='| 标的 | 当日 | 近5交易日 | 近21交易日 | 50日均线（美元） | 200日均线（美元） | 当日/前20日均量 |\n| --- | --- | --- | --- | --- | --- | --- |\n'
rows=[]
for sym in OBSERVATION_SYMBOLS:
 r=metrics[sym];rows.append(f"| {r['label']} | {r['day_pct']:+.2f}% | {r['five_session_pct']:+.2f}% | {r['twenty_one_session_pct']:+.2f}% | {r['ma50']:.2f} | {r['ma200']:.2f} | {r['volume_vs_prior20']:.2f}倍 |")
book['完整表现与趋势数据']=re.sub(r'\| 标的 \| 当日 \| 近5交易日 \|[\s\S]*?(?=\n\n)',head+'\n'.join(rows),book['完整表现与趋势数据'],count=1)
book['口径、核验和缺口'] += '\n分类与展示以[分组总表数据](./watchlist_table.json)为准；本次新增四个常规收盘跨源核验见[分类调整核验](./grouped_watchlist_verification.json)。页面使用现有横向滚动表格；内置浏览器对本地文件的自动导航被策略阻止，本次未绕过该限制做界面复验。\n'
order=['Google估值结果','SOFI研究观察','机器人供应链筛选','行业观察','🔎 Reddit 投资与信息差观察','对你当前状态的建议','距观察档还有多远','利率与未来一周事件','完整表现与趋势数据','口径、核验和缺口']
out=intro+'**今天对你最重要的事**\n'+book['今天对你最重要的事']+'\n'+(P/'watchlist_table.md').read_text()+f'![近60个交易日走势与逐日滚动回撤]({P}/watchlist_curves.png)\n\n'
for title in order:out+='**'+title+'**\n'+book[title]+'\n'
source.write_text(out)
verify={'status':'content_checked','updated_at_utc':datetime.now(timezone.utc).isoformat(),'rows':len(OBSERVATION_SYMBOLS),'groups':['重点指数ETF','机器人相关','AI／半导体','金融科技','价值与综合经营','现金管理'],'unique_primary_category_per_symbol':True,'original_alert_contract_preserved':['QQQ','QQQM','VOO','BRK.B'],'new_regular_closes_cross_checked':{'RRX':161.09,'CGNX':58.43,'ATS':19.17,'NVDA':215.38},'secondary_source_urls':{sym:f'https://stockanalysis.com/stocks/{sym.lower()}/history/' for sym in ['RRX','CGNX','ATS','NVDA']},'price_session':'2026-10-28','price_unit':'USD','not_a_new_investment_recommendation':True,'ui_visual_recheck':'blocked by previously observed Browser Use file URL policy; no bypass','report_markdown_sha256':hashlib.sha256(out.encode()).hexdigest()}
for sym,value in verify['new_regular_closes_cross_checked'].items():assert metrics[sym]['close']==value
(P/'grouped_watchlist_verification.json').write_text(json.dumps(verify,ensure_ascii=False,indent=2)+'\n')
print('one categorized table inserted before company details',len(OBSERVATION_SYMBOLS))
