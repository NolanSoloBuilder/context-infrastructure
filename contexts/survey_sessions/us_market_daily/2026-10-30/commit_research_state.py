from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
P=Path(__file__).resolve().parent;root=P.parent;now=datetime.now(timezone.utc).isoformat()
m={r['symbol']:r for r in json.loads((P/'metrics.json').read_text())};v=json.loads((P/'verification.json').read_text());h=json.loads((P/'html_verification.json').read_text());assert v['status']=='passed_with_disclosed_gaps' and all(h['static_checks'].values())
# Only the original four-symbol contract is advanced, after report persistence and quote verification.
sp=root/'alert_state.json';s=json.loads(sp.read_text());assert s['last_checked_session']<='2026-10-29';before=s['last_checked_session'];changed=[]
if before<'2026-10-29':
 for label,symbol in [('QQQ','QQQ'),('QQQM','QQQM'),('VOO','VOO'),('BRK.B','BRK-B')]:
  r=m[symbol];d=-r['drawdown_pct'];stage='below_13' if d<13 else 'near_15' if d<15 else 'at_or_above_15' if d<23 else 'near_25' if d<25 else 'at_or_above_25';old=s['symbols'][label];prior=old['stage'];highlight=stage!=prior and stage!='below_13'
  if highlight:changed.append(label)
  if stage!=prior:old['stage_since_session']='2026-10-29'
  old.update(last_checked_session='2026-10-29',close_usd=r['close'],high_52w_usd=r['high_52w'],high_date=r['high_date'],drawdown_pct=d,stage=stage,previous_stage=prior,new_highlight=highlight,level_15_usd=r['level_15'],level_25_usd=r['level_25'],gap_to_15_percentage_points=15-d,price_change_to_15_pct=r['additional_drop_to_15_pct'])
  if highlight:old['last_highlight_report_date']='2026-10-30'
 s.update(last_checked_session='2026-10-29',report_date_beijing='2026-10-30',updated_at_utc=now,highlighted_symbols=changed)
 s['data_validation'].update(watchlist_closes_verified=True,watchlist_highs_verified_with_disclosed_qqqm_one_cent_difference=True,verification_file=str(P/'verification.json'),report_file=str(P/'report.md'),report_sha256=hashlib.sha256((P/'report.md').read_bytes()).hexdigest(),report_html_file=str(P/'report.html'))
 sp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
assert set(s['symbols'])=={'QQQ','QQQM','VOO','BRK.B'} and not changed
# Selected Reddit items only: incomplete feed coverage is retained as a limitation.
rp=root/'reddit_state.json';rs=json.loads(rp.read_text());src=json.loads((P/'reddit_sources.json').read_text());ids=[]
for item in src['selected_items']:
 key=item['item_id'];assert key not in rs['reported_items'] or rs['reported_items'][key].get('last_report_date_beijing')=='2026-10-30'
 assert item['post_url'] in (P/'report.md').read_text();ids.append(key)
 rs['reported_items'][key]={'post_id':item['post_ids'][0],'post_ids':item['post_ids'],'post_url':item['post_url'],'source_urls':item['source_urls'],'first_report_date_beijing':'2026-10-30','last_report_date_beijing':'2026-10-30','reported_in_digest_at_utc':now,'digest_path':str(P/'reddit_digest.md'),'freshness_status':'original_bodies_comments_read_but_absolute_post_time_and_full24h_coverage_unverified','claim_keys':[r['claim'] for r in item['key_claims']],'classification':item['classification'],'next_check':item['next_check']}
runid='2026-10-30-daily'
rs['runs']=[r for r in rs['runs'] if r['run_id']!=runid]+[{'run_id':runid,'type':'daily_heartbeat','collection_cutoff_at_utc':src['collected_at_utc'],'artifact_saved_at_utc':now,'coverage_status':src['coverage_status'],'complete_reddit_scan':False,'reported_item_ids':ids,'digest_path':str(P/'reddit_digest.md'),'source_record_path':str(P/'reddit_sources.json'),'digest_sha256':hashlib.sha256((P/'reddit_digest.md').read_bytes()).hexdigest()}]
rs.update(last_successful_check_at_utc=src['collected_at_utc'],last_successful_check_scope='Selected original Google posts and substantive supporting/contrary comments only; absolute post times/full24h scan not verified; stale feeds and archive challenges retained',last_run_id=runid);rp.write_text(json.dumps(rs,ensure_ascii=False,indent=2)+'\n')
# Fresh model facts replace the active model reference; archived entry-price bands remain suspended.
p=root/'valuation_research_watch.json';x=json.loads(p.read_text());g=json.loads((P/'google_update/google_valuation_model.json').read_text());old=x['google']
if 'archived_2026_10_28_model' not in old:old['archived_2026_10_28_model']={k:old[k] for k in ['baseline_dcf','bear','bull','model']}
old.update(baseline_dcf=g['scenarios'][1]['price_usd'],bear=g['scenarios'][0]['price_usd'],bull=g['scenarios'][2]['price_usd'],model='2026-10-30/google_update/google_valuation_model.json',entry_ranges_validity='SUSPENDED_OLD_RANGES_PENDING_NEW_ENTRY_PLAN',new_complete_dcf_available=True,latest_quote_session_us='2026-10-29',latest_regular_close_usd=283.82,latest_update_file='2026-10-30/google_update/google_update.md',latest_model_status='Q3 financial facts and major capital bridge updated; future forecasts retain prior analyst assumptions; not approved price targets or allocation',note='Old entry ranges are archived and remain suspended. Complete ten-year model rerun using latest major Q3 facts, with forward TPU/Cloud economics and capital spending still conditional; do not use price decline or model point estimate as automatic entry.',latest_call_findings={'source_scope':'Official CEO remarks plus third-party full CFO/Q&A transcript; Q3 10-Q now read and archived','valuation_gaps':['Forward TPU versus service economics','Working-capital and cash conversion path','Q4 margin after external compute ramp','2027 spending and dilution scenarios'],'entry_price_policy':'No new entry bands approved or activated','cashflow_correction':'Q3 inventoryCFO -3.220B is total company, not TPU-only; working-capital and capex kept separate'})
x.update(research_date_beijing='2026-10-30',quote_session_us='2026-10-29',latest_review_date_beijing='2026-10-30');p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
p=root/'research_policy.md';text=p.read_text().replace('更新：2026-10-29。','更新：2026-10-30。',1).replace('- 预算、最大可接受亏损、确定用款日期及税务身份尚未补齐。40%股票/60%防守、首笔10%及后续月度分批均为未确认草案。','- 已确认预算30,000美元、可接受约6,000美元（20%）暂时亏损、境外资金无需急用；确定用款日期与税务身份未知。最新45%股票/55%SGOV、首笔10%及后续分批均为未确认草案，无持仓确认。')
marker='## 2026-10-30研究进展'
if marker not in text:text+='\n'+marker+'\n\nQ3完整10-Q已取得并存档，资本桥与十年模型主要财务事实更新完成，见2026-10-30/google_update/google_update.md及google_valuation_model.json。68.25/216.28/402.11为保留主观经营假设的三情景，不是确定合理价；旧入场档继续暂停，后续推进服务/TPU经济性、外部算力成本、营运资金和2027支出，不能继续用尚缺完整10-Q拖延研究。SOFI新增有形资本回报压力检验，仍非完整估值；见同日日报sofi_research.md。GDP/PCE已公布，10/30研究判断为可考虑小额时间分批、暂不加速，未获采用与未确认成交边界不变。用户可能快进快出，暂未明确具体策略，不据此变更期限或扩大风险预算。\n'
p.write_text(text)
print(json.dumps({'original_alert_session_advanced_from':before,'now_session':s['last_checked_session'],'new_highlights':changed,'reddit_items_recorded':ids,'old_entry_ranges':'still_suspended','trades':0},ensure_ascii=False))
