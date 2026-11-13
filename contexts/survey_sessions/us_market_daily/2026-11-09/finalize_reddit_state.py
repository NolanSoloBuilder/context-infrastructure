"""Record only the verified NVDA claim after successful public publication."""
from pathlib import Path
from datetime import datetime, timezone
import copy
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
def read(path):
    return json.loads(path.read_text())
def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

receipt = read(HERE / 'publish/deployment_receipt.json')
deployment = receipt['deployment']
assert deployment['status'] == 'succeeded'
brief = read(HERE / 'publish/live_state_after_deploy.json')['daily_brief']
assert brief['report_date'] == '2026-11-09' and brief['market_session'] == '2026-11-06'
source = read(HERE / 'reddit_sources.json')
proposal = read(HERE / 'reddit_state_update_proposal.json')
urls = {x['url'] for section in brief['sections'] for x in section.get('sources', [])}
assert 'https://nvidianews.nvidia.com/news/statement-from-nvidia-board-of-directors' in urls
state_path = BASE / 'reddit_state.json'
state = read(state_path)
old = copy.deepcopy(state)
if not (HERE / 'reddit_state_before.json').exists():
    save(HERE / 'reddit_state_before.json', old)
now = datetime.now(timezone.utc).isoformat()
reported = []
for item in source['items']:
    canonical = item['url'].split('/comments/')[0] + '/comments/' + item['id'] + '/'
    if canonical not in urls and item['url'] not in urls:
        continue
    key = item['claim_key']
    prior = state['reported_items'].get(key, {})
    state['reported_items'][key] = {
        'post_id': item['id'], 'post_ids': [item['id']], 'post_url': canonical,
        'claim_keys': [key],
        'first_report_date_beijing': prior.get('first_report_date_beijing', '2026-11-09'),
        'last_report_date_beijing': '2026-11-09', 'reported_in_digest_at_utc': now,
        'digest_path': str(HERE / 'reddit_digest.md'), 'source_record_path': str(HERE / 'reddit_sources.json'),
        'classification': item['classification'], 'read_scope': item['read_scope'],
        'comments_status': item['comments_status'], 'published_url': deployment['url'],
        'published_version_id': deployment['version_id'], 'full_scan_complete': False,
        'reported_scope': 'Only official investigation, board position and financial uncertainty; anonymous allegations excluded',
    }
    reported.append(key)
assert len(reported) == 1
run = {
    'run_id': '2026-11-09-daily', 'type': 'daily_heartbeat',
    'collection_cutoff_at_utc': proposal['cutoff_utc'], 'artifact_saved_at_utc': now,
    'coverage_status': 'partial_public_access_one_officially_verified_new_claim',
    'complete_reddit_scan': False, 'reported_item_ids': reported,
    'digest_path': str(HERE / 'reddit_digest.md'), 'source_record_path': str(HERE / 'reddit_sources.json'),
    'digest_sha256': hashlib.sha256((HERE / 'reddit_digest.md').read_bytes()).hexdigest(),
    'published_version_id': deployment['version_id'],
}
state['runs'] = [x for x in state['runs'] if x.get('run_id') != run['run_id']] + [run]
state.update(last_run_id=run['run_id'], last_successful_partial_read_at_utc=proposal['partial_check_at_utc'],
    last_attempt=run, last_attempt_at_utc=proposal['partial_check_at_utc'],
    last_attempt_report_date='2026-11-09', last_attempt_status='partial_read_published')
assert state['last_successful_check_at_utc'] == old['last_successful_check_at_utc']
tmp = state_path.with_suffix('.json.tmp')
save(tmp, state)
tmp.replace(state_path)
save(HERE / 'reddit_state_after.json', state)
save(HERE / 'reddit_publication.json', {'published_at': now, 'version_id': deployment['version_id'], 'reported_claim_keys': reported,
    'full_scan_complete': False, 'prior_successful_check_timestamp_preserved': True,
    'fiNews_status': proposal['fiNews_status'], 'editorial_correction': 'Independent directors oversee; independent outside counsel assists, as reflected in published brief and card.'})
print(json.dumps({'published_claims': len(reported), 'full_scan_complete': False}, ensure_ascii=False))
