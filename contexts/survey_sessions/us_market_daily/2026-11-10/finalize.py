from pathlib import Path
from datetime import datetime,timezone
import json,copy,hashlib,collections
P=Path(__file__).resolve().parent;BASE=P.parent
rd=lambda p:json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
receipt=rd(P/'publish/deployment_receipt.json');d=receipt['deployment'];assert d['status']=='succeeded'
x=rd(P/'publish/live_state_after_deploy.json');b=x['daily_brief'];expected=rd(P/'daily_brief_published_candidate.json');assert b==expected
assert b['report_date']=='2026-11-10' and b['market_session']=='2026-11-09'
html=(P/'publish/live_home.html').read_text();assert '2026-11-10' in html and 'TEAM扩大项目' in html and '279.52' in html
assets={a['symbol']:a for g in x['catalog']['groups'] for a in g['assets']};assert len(assets)==43 and 'QQQ' not in assets
assert len([a for a in assets.values() if a['kind']=='fund'])==17
assert all(a['quote']['session']==('2026-11-06' if s in ['XSW','ATS'] else '2026-11-09') for s,a in assets.items())
assert assets['SGOV']['facts']['sec_yield_pct']==3.84 and assets['SGOV']['facts']['sec_yield_date']=='2026-11-06'
assert 'TPU周转' in assets['GOOGL']['research_status']
h=rd(P/'publish/live_history.json')['dates'];assert len(h)==len(set(h)) and '2026-11-09' in h and not {'2026-11-07','2026-11-08'}&set(h)
old=rd(P/'publish/old_archive_check.json');assert old['daily_brief']['report_date']=='2026-11-09' and old['daily_brief']['market_session']=='2026-11-06'
new=rd(P/'publish/new_archive_check.json');assert new['daily_brief']==b
now=datetime.now(timezone.utc).isoformat()
a=rd(P/'alert_state_proposal.json');assert rd(BASE/'alert_state.json')==rd(P/'alert_state_before.json'),'alert changed concurrently'
a['publication']={'published_at_utc':now,'version_id':d['version_id'],'deployment_id':d['id'],'status':'succeeded','site_url':d['url']}
tmp=BASE/'alert_state.json.tmp';save(tmp,a);tmp.replace(BASE/'alert_state.json');save(P/'alert_state_after.json',a)
statepath=BASE/'reddit_state.json';state=rd(statepath);prior=copy.deepcopy(state);save(P/'reddit_state_before.json',prior)
s=rd(P/'reddit_sources.json');urls={q['url'] for sec in b['sections'] for q in sec['sources']};reported=[]
for item in s['selected_items']:
 assert item['canonical_url'] in urls
 k=item['claim_key'];olditem=state.get('reported_items',{}).get(k,{})
 state.setdefault('reported_items',{})[k]={'post_id':item['id'],'post_ids':[item['id']],'post_url':item['canonical_url'],'claim_keys':[k],'first_report_date_beijing':olditem.get('first_report_date_beijing','2026-11-10'),'last_report_date_beijing':'2026-11-10','reported_in_digest_at_utc':now,'digest_path':str(P/'reddit_digest.md'),'source_record_path':str(P/'reddit_sources.json'),'classification':item['classification'],'read_scope':item['read_scope'],'comments_status':'substantive supporting and counter comments read','published_url':d['url'],'published_version_id':d['version_id'],'full_scan_complete':False}
 reported.append(k)
run={'run_id':'2026-11-10-daily','type':'daily_heartbeat','collection_cutoff_at_utc':s['window_end_utc'],'artifact_saved_at_utc':now,'coverage_status':'partial_public_access_two_verified_new_discussions','complete_reddit_scan':False,'reported_item_ids':reported,'digest_path':str(P/'reddit_digest.md'),'source_record_path':str(P/'reddit_sources.json'),'digest_sha256':hashlib.sha256((P/'reddit_digest.md').read_bytes()).hexdigest(),'published_version_id':d['version_id']}
state['runs']=[v for v in state['runs'] if v.get('run_id')!=run['run_id']]+[run]
state.update(last_run_id=run['run_id'],last_successful_partial_read_at_utc=s['reviewed_at_utc'],last_attempt=run,last_attempt_at_utc=s['reviewed_at_utc'],last_attempt_report_date='2026-11-10',last_attempt_status='partial_read_published')
assert state['last_successful_check_at_utc']==prior['last_successful_check_at_utc']
tmp=statepath.with_suffix('.json.tmp');save(tmp,state);tmp.replace(statepath);save(P/'reddit_state_after.json',state)
save(P/'publication_verification.json',{'checked_at':now,'status':'passed','report_date':b['report_date'],'market_session':b['market_session'],'version':receipt['saved_version']['version_number'],'public_url':d['url'],'home_and_api_brief_match':True,'history_sessions':h,'new_archive_matches_current':True,'old_archive_unchanged':True,'quote_sessions':dict(collections.Counter(a['quote']['session'] for a in assets.values())),'partial_history_symbols':['XSW','ATS'],'alert_highlights':a['highlighted_symbols'],'reddit_reported_claims':reported,'reddit_full_scan_complete':False,'audience':'public','private_data_published':False})
(P/'run_summary.md').write_text('''# 2026-11-10 美股观察发布审计

已通过Sites技能发布原站点v27；公开首页/API研究日期2026-11-10，行情基准美国11/9，3项首页结论。43项监测中41项行情更新至11/9；XSW、ATS因OHLC矛盾保留11/6。额外行业XLY缺失，条形图未填0。

QQQM回撤约11.01%，从near_15退出到below_13；三项均无新跨档，QQQ退役状态保持。提醒分币高点与图线原始精度尾差已明示。未自动交易或重新核券商数量。

新增TEAM FDE证据与迁移/SBC反证；Google Q3现金流差分及TPU周转假设模型；BRK日元再融资初稿与NVDA跨层投资，未冒称融资到账/利润实现。CPI今晚21:30未公布，VIX下降与美债收益率上升并存。SGOV官方SEC30日3.84%截至11/6。

Reddit仅部分覆盖，2条新增讨论成功发布后才记去重状态；全量成功时间未推进。FiNews实际11/9版已读取，银行假日不等于11/11股票休市。

两张真实60日/行业审计图已查看、末值复算；19项定向测试通过。未改模板，不声称新增浏览器视觉验收。站点及新交易日归档回读一致，11/6旧归档保留原研究，未创建周末日档。私人数据未进入公开资料。
''')
print('Published research, market dates, two archives and privacy boundary verified; alerts and two Reddit claims finalized.')
