from pathlib import Path
from datetime import datetime,timezone
import json,copy,hashlib,collections
P=Path(__file__).resolve().parent;BASE=P.parent
rd=lambda p:json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
r=rd(P/'publish/deployment_receipt.json');d=r['deployment'];assert d['status']=='succeeded'
x=rd(P/'publish/live_state_after_deploy.json');b=x['daily_brief'];expected=rd(P/'daily_brief_published_candidate.json');assert b==expected
assert b['report_date']=='2026-11-11' and b['market_session']=='2026-11-10'
assert x['refresh_status']['status']=='complete' and x['refresh_status']['successful_history_symbols']==43
html=(P/'publish/live_home.html').read_text()
for v in ['2026-11-11','CPI已公布','CoreWeave','277.87','独立调查']:assert v in html,v
assets={a['symbol']:a for g in x['catalog']['groups'] for a in g['assets']};assert len(assets)==43
assert len([a for a in assets.values() if a['kind']=='fund'])==17
assert not set(assets)&{'QQQ','PDD','DDL','BABA','XPEV','TCEHY','KWEB'}
assert all(a['quote']['session']=='2026-11-10' for a in assets.values())
m={a['symbol']:a for a in rd(P/'metrics.json')}
assert all(a['quote']['close']==m[s]['close'] for s,a in assets.items())
assert assets['SGOV']['facts']['sec_yield_pct']==3.85 and assets['SGOV']['facts']['sec_yield_date']=='2026-11-09'
assert assets['NVDA']['facts']['governance_event']['latest_event_date']=='2026-11-10'
assert '已签5亿美元ASR' in json.dumps(assets['EPAM'],ensure_ascii=False)
privacy_html=html.replace('本云端观察台不连接券商，不上传账户号、持仓股数、实际成本或登录信息。','')
for v in ['portfolio_private','30,000','30000美元','账户号','我的持仓','已持有GOOG']:
 assert v not in privacy_html and v not in json.dumps(x,ensure_ascii=False),v
h=rd(P/'publish/live_history.json')['dates'];assert len(h)==len(set(h)) and '2026-11-10' in h and not {'2026-11-07','2026-11-08'}&set(h)
old=rd(P/'publish/old_archive_check.json');assert old==rd(P/'publish/old_archive_before.json')
assert old['daily_brief']['report_date']=='2026-11-10' and old['daily_brief']['market_session']=='2026-11-09'
new=rd(P/'publish/new_archive_check.json');assert new['daily_brief']==b
assert all(a['quote']['session']=='2026-11-10' for g in new['catalog']['groups'] for a in g['assets'])
now=datetime.now(timezone.utc).isoformat()
a=rd(P/'alert_state_proposal.json');assert rd(BASE/'alert_state.json')==rd(P/'alert_state_before.json'),'concurrent alert write'
a['publication']={'published_at_utc':now,'version_id':d['version_id'],'deployment_id':d['id'],'status':'succeeded','site_url':d['url']}
tmp=BASE/'alert_state.json.tmp';save(tmp,a);tmp.replace(BASE/'alert_state.json');save(P/'alert_state_after.json',a)
statepath=BASE/'reddit_state.json';state=rd(statepath);prior=copy.deepcopy(state);save(P/'reddit_state_before.json',prior)
s=rd(P/'reddit_sources.json');assert not s['selected_items'] and s['full_scan_complete'] is False
run={'run_id':'2026-11-11-daily','type':'daily_heartbeat','collection_cutoff_at_utc':s['target_window_end_utc'],'artifact_saved_at_utc':now,'coverage_status':s['status'],'complete_reddit_scan':False,'reported_item_ids':[],'digest_path':str(P/'reddit_digest.md'),'source_record_path':str(P/'reddit_sources.json'),'digest_sha256':hashlib.sha256((P/'reddit_digest.md').read_bytes()).hexdigest(),'published_version_id':d['version_id'],'reason':'Access and absolute-date gaps published; no new Reddit claim recorded.'}
state['runs']=[v for v in state['runs'] if v.get('run_id')!=run['run_id']]+[run]
state.update(last_run_id=run['run_id'],last_attempt=run,last_attempt_at_utc=s['reviewed_at_utc'],last_attempt_report_date='2026-11-11',last_attempt_status='partial_access_gaps_published_no_new_claims')
for k in ['last_successful_check_at_utc','last_successful_partial_read_at_utc','reported_items']:assert state.get(k)==prior.get(k)
tmp=statepath.with_suffix('.json.tmp');save(tmp,state);tmp.replace(statepath);save(P/'reddit_state_after.json',state)
save(P/'publication_verification.json',{'checked_at':now,'status':'passed','report_date':b['report_date'],'market_session':b['market_session'],'version':r['saved_version']['version_number'],'public_url':d['url'],'home_and_api_brief_match':True,'history_sessions':h,'new_archive_matches_current':True,'old_archive_byte_content_equivalent':True,'quote_sessions':dict(collections.Counter(v['quote']['session'] for v in assets.values())),'quote_closes_match_local_audit':True,'alert_highlights':a['highlighted_symbols'],'reddit_new_reported_claims':[],'reddit_full_scan_complete':False,'audience':'public','private_data_published':False})
(P/'run_summary.md').write_text('''# 2026-11-11 发布审计

原站点v28成功发布；首页及API研究日期北京11/11，行情美国11/10，43/43当日行情有效。XSW/ATS与额外行业XLY本次来源序列校验通过，不再沿用昨日缺口。新11/10归档研究与首页一致，11/9旧归档内容未改，无周末重复档。

三项观察均below_13无新触发。QQQM回撤11.54%；BRK.B高点更新至Yahoo586.41/StockAnalysis586.45，同为11/10，来源差异不改变分档。到观察价的价格变化按显示美分价格计算。

首页：CPI总环比0.4%、核心0.3%，同比正式缺失；利率压力；NVDA11/10聘请独立调查律师；CoreWeave盘后现金桥与AI应用/基础设施并行的反证。EPAM ASR签约状态和SGOV SEC30日3.85%截至11/9同步卡片。旧估值保留原假设日期。未新增标的或交易。

Reddit部分读取，六RSS403且原帖绝对日期不足，新增精选0，不推进全量/合格部分成功时间、不登记新报道主张。FiNews11/10版实际读取，NYFed事实回查官方，11/11股票休市误述已纠正。

19项定向测试通过，brief与部署产物验证通过；两张审计图已实际查看及末值复算。仅内容更新，未声称新增浏览器视觉验收。公共文件无私人预算、数量、成本或实际持仓。
''')
print('v28 live content, 43 quotes, archive isolation and privacy verified; alert and attempt-only Reddit state finalized.')
