from pathlib import Path
from datetime import datetime,timezone
import json,copy,hashlib,collections
P=Path(__file__).resolve().parent;BASE=P.parent
rd=lambda p:json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
r=rd(P/'publish/deployment_receipt.json');d=r['deployment'];assert d['status']=='succeeded'
x=rd(P/'publish/live_state_after_deploy.json');b=x['daily_brief'];expected=rd(P/'daily_brief_published_candidate.json');assert b==expected
assert b['report_date']=='2026-11-12' and b['market_session']=='2026-11-11'
assert x['refresh_status']['status']=='complete' and x['refresh_status']['successful_history_symbols']==43
html=(P/'publish/live_home.html').read_text()
for v in ['2026-11-12','NVDA盘后明显下跌','CoreWeave','284.23','160.24']:assert v in html,v
assets={a['symbol']:a for g in x['catalog']['groups'] for a in g['assets']};assert len(assets)==43
assert len([a for a in assets.values() if a['kind']=='fund'])==17
assert not set(assets)&{'QQQ','PDD','DDL','BABA','XPEV','TCEHY','KWEB'}
assert all(a['quote']['session']=='2026-11-11' for a in assets.values())
m={a['symbol']:a for a in rd(P/'metrics.json')}
diffs=[{'symbol':s,'local':m[s]['close'],'cloud':a['quote']['close'],'delta_usd':round(a['quote']['close']-m[s]['close'],4)} for s,a in assets.items() if a['quote']['close']!=m[s]['close']]
assert all(z['symbol']=='MSFT' and abs(z['delta_usd'])<=.011 for z in diffs),diffs
assert assets['SGOV']['facts']['sec_yield_pct']==3.85 and assets['SGOV']['facts']['sec_yield_date']=='2026-11-10'
privacy_html=html.replace('本云端观察台不连接券商，不上传账户号、持仓股数、实际成本或登录信息。','')
for v in ['portfolio_private','30,000','30000美元','账户号','我的持仓','已持有GOOG']:assert v not in privacy_html and v not in json.dumps(x,ensure_ascii=False),v
h=rd(P/'publish/live_history.json')['dates'];assert len(h)==len(set(h)) and '2026-11-11' in h and not {'2026-11-07','2026-11-08'}&set(h)
old=rd(P/'publish/old_archive_check.json');assert old==rd(P/'publish/old_archive_before.json')
assert old['daily_brief']['report_date']=='2026-11-11' and old['daily_brief']['market_session']=='2026-11-10'
new=rd(P/'publish/new_archive_check.json');assert new['daily_brief']==b
assert all(a['quote']['session']=='2026-11-11' for g in new['catalog']['groups'] for a in g['assets'])
now=datetime.now(timezone.utc).isoformat();a=rd(P/'alert_state_proposal.json')
assert rd(BASE/'alert_state.json')==rd(P/'alert_state_before.json'),'concurrent alert write'
a['publication']={'published_at_utc':now,'version_id':d['version_id'],'deployment_id':d['id'],'status':'succeeded','site_url':d['url']}
tmp=BASE/'alert_state.json.tmp';save(tmp,a);tmp.replace(BASE/'alert_state.json');save(P/'alert_state_after.json',a)
statepath=BASE/'reddit_state.json';state=rd(statepath);prior=copy.deepcopy(state);save(P/'reddit_state_before.json',prior)
s=rd(P/'reddit_sources.json');assert not s['selected_items'] and s['full_scan_complete'] is False
run={'run_id':'2026-11-12-daily','type':'daily_heartbeat','collection_cutoff_at_utc':s['target_window']['cutoff_utc'],'artifact_saved_at_utc':now,'coverage_status':s['status'],'complete_reddit_scan':False,'reported_item_ids':[],'digest_path':str(P/'reddit_digest.md'),'source_record_path':str(P/'reddit_sources.json'),'digest_sha256':hashlib.sha256((P/'reddit_digest.md').read_bytes()).hexdigest(),'published_version_id':d['version_id'],'reason':'Access and absolute-date gaps published; no new Reddit claim recorded.'}
state['runs']=[v for v in state['runs'] if v.get('run_id')!=run['run_id']]+[run]
state.update(last_run_id=run['run_id'],last_attempt=run,last_attempt_at_utc=s['collected_at'],last_attempt_report_date='2026-11-12',last_attempt_status='partial_access_gaps_published_no_new_claims')
for k in ['last_successful_check_at_utc','last_successful_partial_read_at_utc','reported_items']:assert state.get(k)==prior.get(k)
tmp=statepath.with_suffix('.json.tmp');save(tmp,state);tmp.replace(statepath);save(P/'reddit_state_after.json',state)
save(P/'publication_verification.json',{'checked_at':now,'status':'passed','report_date':b['report_date'],'market_session':b['market_session'],'version':r['saved_version']['version_number'],'public_url':d['url'],'home_and_api_brief_match':True,'history_sessions':h,'new_archive_matches_current':True,'old_archive_content_unchanged':True,'quote_sessions':dict(collections.Counter(v['quote']['session'] for v in assets.values())),'quote_differences_disclosed':diffs,'alert_highlights':a['highlighted_symbols'],'reddit_new_reported_claims':[],'reddit_full_scan_complete':False,'audience':'public','private_data_published':False})
(P/'run_summary.md').write_text('''# 2026-11-12 发布审计

原站点新版本成功发布；首页及API研究日期北京11/12，行情美国11/11，43/43当日行情有效。MSFT本地521.12与云端/第二源521.13差0.01美元已说明。11/11新归档研究匹配首页，11/10旧归档内容未改，无周末重复。

三项观察均below_13，无新触发。QQQM回撤9.51%，BRK.B高点Yahoo588.48/StockAnalysis588.54，同为11/11且差异不改变档位，观察价500.21/441.36。60日真实曲线与12行业图已实际检查和独立复算。

首页：NVDA盘后Yahoo160.24(-7.76%,18:29EST)/StockAnalysis159.46(-8.21%,18:27EST)，差异与零量参考声明保留，不把传闻归因为已证实经营损害；QQQM收复MA200但量弱；CRWV新数据库与旧GPU续约反证及24亿/60亿美元条件敏感性，非FCF/订单。SGOV仅官方截至日推进11/10，收益率3.85%未变。四股模型及Google/SOFI旧日期保留，不假称全量重估。

Reddit部分读取，RSS403和原帖绝对日期缺口，新增精选0，不推进成功时间或新报道主张。FiNews11/11已读；FDE原文补核日期未知，非当日催化。公开源码无私人数据。19项定向测试通过，真实部署与API验收通过；内容更新未声称新增浏览器视觉验收。
''')
print('Live publication verified: 43 current sessions, dated brief, archive isolation, privacy; alert and Reddit attempt states finalized.')
