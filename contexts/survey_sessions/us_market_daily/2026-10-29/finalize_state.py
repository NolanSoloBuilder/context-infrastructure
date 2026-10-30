from pathlib import Path
from datetime import datetime,timezone
from html.parser import HTMLParser
import json,hashlib,re
P=Path(__file__).resolve().parent;root=P.parent
now=datetime.now(timezone.utc).isoformat()
html=(P/'report.html').read_text();md=(P/'report.md').read_text();checks=json.loads((P/'verification.json').read_text());hm=json.loads((P/'html_manifest.json').read_text())
assert checks['session']=='2026-10-28' and checks['historical_drawdown_points_recomputed_without_lookahead']==180
assert '2026-10-29' in html and '2026-10-28' in html
for price in ['725.61','298.71','709.90','540.34','324.89','161.09']:assert price in html,price
for section in ['今天对你最重要的事','主观察表','Google估值结果','机器人供应链筛选','Reddit','利率与事件日历']:assert section in html,section
assert html.count('<figure>')==3 # two fresh daily charts, one explicitly dated previous model chart in appendix
assert html.count('data:image/png;base64,')>=2
for url in ['https://www.sec.gov/Archives/edgar/data/1652044/000165204426000080/googexhibit991q32026.htm','https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm','https://www.reddit.com/r/MSFT/comments/1xg87kw/','https://finews.fyi/']:assert url in html,url
# Offline HTML must not initiate remote scripts/styles or carry raw local MD paths as sources.
assert not re.search(r'<script[^>]+src=[\"\']https?://',html)
assert '2026-10-29/watchlist_curves.png' not in html
mc=json.loads((P/'market_context.json').read_text());mc['news_cutoff_recorded_at_utc']=now;mc.pop('news_cutoff',None);(P/'market_context.json').write_text(json.dumps(mc,ensure_ascii=False,indent=2)+'\n')
# The changed evidence attachment requires a fresh conversion after this script.
old=json.loads((root/'alert_state.json').read_text());(P/'alert_state_before.json').write_text(json.dumps(old,indent=2,ensure_ascii=False)+'\n')
m={r['symbol']:r for r in json.loads((P/'metrics.json').read_text())}
assert old['last_checked_session']<='2026-10-28'
if old['last_checked_session']<'2026-10-28':
 new=json.loads(json.dumps(old));new.update(last_checked_session='2026-10-28',report_date_beijing='2026-10-29',updated_at_utc=now)
 for key,s in [('QQQ','QQQ'),('QQQM','QQQM'),('VOO','VOO'),('BRK.B','BRK-B')]:
  r=m[s];D=-r['drawdown_pct'];stage='below_13' if D<13 else 'near_15' if D<15 else 'at_or_above_15' if D<23 else 'near_25' if D<25 else 'at_or_above_25'
  prior=old['symbols'][key];n=new['symbols'][key]
  n.update(last_checked_session='2026-10-28',close_usd=r['close'],high_52w_usd=r['high_52w'],high_date=r['high_date'],drawdown_pct=D,previous_stage=prior['stage'],stage=stage,new_highlight=False,level_15_usd=r['level_15'],level_25_usd=r['level_25'],gap_to_15_percentage_points=15-D,price_change_to_15_pct=r['additional_drop_to_15_pct'])
  assert stage=='below_13' and prior['stage']==stage # current run has no triggers
 new['highlighted_symbols']=[]
 new['data_validation'].update(verification_file=str(P/'verification.json'),report_file=str(P/'report.md'),report_html_file=str(P/'report.html'),report_sha256=hashlib.sha256(md.encode()).hexdigest())
 (root/'alert_state.json').write_text(json.dumps(new,indent=2,ensure_ascii=False)+'\n')
# Mark only successfully read and actually saved items. Failed feeds never become reported claims.
rsfile=root/'reddit_state.json';rs=json.loads(rsfile.read_text());(P/'reddit_state_before.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2)+'\n')
sources=json.loads((P/'reddit_sources.json').read_text());assert len(sources['items'])==2 and (P/'reddit_digest.md').stat().st_size>100
if rs.get('last_run_id')!='2026-10-29-daily':
 for item in sources['items']:
  k=item['item_id'];entry={key:item.get(key) for key in ['post_id','post_url','source_url','community','claim_keys','classification','freshness_status','next_check']}
  entry.update(first_report_date_beijing='2026-10-29',last_report_date_beijing='2026-10-29',reported_in_digest_at_utc=now,digest_path=str(P/'reddit_digest.md'),exact_post_time_beijing=None)
  rs.setdefault('reported_items',{})[k]=entry
 rs.setdefault('runs',[]).append({'run_id':'2026-10-29-daily','type':'daily_heartbeat','collection_cutoff_at_utc':sources['collection_at_utc'],'artifact_saved_at_utc':now,'coverage_status':'partial_public_read_with_stale_feed_and_timestamp_gaps','complete_reddit_scan':False,'reported_item_ids':[i['item_id'] for i in sources['items']],'digest_path':str(P/'reddit_digest.md'),'source_record_path':str(P/'reddit_sources.json'),'digest_sha256':hashlib.sha256((P/'reddit_digest.md').read_bytes()).hexdigest()})
 rs.update(last_successful_check_at_utc=sources['collection_at_utc'],last_successful_check_scope='Only selected original public bodies/comments and primary disclosures; fresh-feed scan failed; exact24h/72h window unverified',last_run_id='2026-10-29-daily')
 rsfile.write_text(json.dumps(rs,ensure_ascii=False,indent=2)+'\n')
# Suspend obsolete model entry bands as research status, while retaining their historical inputs.
vfile=root/'valuation_research_watch.json';v=json.loads(vfile.read_text());(P/'valuation_research_watch_before.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
v['latest_review_date_beijing']='2026-10-29';v['google']['entry_ranges_validity']='SUSPENDED_PENDING_Q3_CAPITAL_BRIDGE';v['google']['latest_event_date_us']='2026-10-28';v['google']['latest_quote_session_us']='2026-10-28';v['google']['latest_regular_close_usd']=324.89;v['google']['new_complete_dcf_available']=False;v['google']['latest_update_file']='2026-10-29/google_update/google_update.md';v['google']['note']='Original180-195/160-175/140-155 are archived research ranges; do not use until Q3 assets/debt/leases/claims are reconciled and complete model rebuilt. Partial217.36 sensitivity is not a new fair value.'
v['robotics']['RRX']['latest_review']='2026-10-29/robotics_update.md';v['robotics']['RRX']['new_findings']='9.71 reference EPS still adds back3.92/share acquisition amortization;17x value148.41/131.75 if25%/50% restored, assumptions not validated. RRX current close cross-source has gaps; no entry alert.'
vfile.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
checks['html_validation']={'date_prices_sources_verified':True,'template_changed':False,'new_daily_charts':2,'archived_model_chart_in_explicitly_dated_appendix':1,'no_remote_script_or_style':True,'validated_at_utc':now,'bytes_before_final_conversion':len(html.encode()),'browser_full_layout_not_repeated':'unchanged accepted template; two current PNGs visually inspected'}
(P/'verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'report_date':'2026-10-29','state_session':'2026-10-28','new_drawdown_alerts':[],'reddit_new_selected_items':2,'google_old_ranges_suspended':True,'html_checked':True},ensure_ascii=False))
