"""Mark only successfully published, actually read claims as reported."""
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
def read(path):
    return json.loads(path.read_text())
def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

receipt = read(HERE / 'publish/deployment_receipt.json')
deployment = receipt['deployment']
assert deployment['status'] == 'succeeded'
published = read(HERE / 'publish/live_state_after_deploy.json')['daily_brief']
assert published['report_date'] == '2026-11-08'
source = read(HERE / 'reddit_sources.json')
proposal = read(HERE / 'reddit_state_update_proposal.json')
state_path = BASE / 'reddit_state.json'
state = read(state_path)
old = copy.deepcopy(state)
before_path = HERE / 'reddit_state_before.json'
if not before_path.exists():
    save(before_path, old)
urls = {s['url'] for section in published['sections'] for s in section.get('sources', [])}
now = datetime.now(timezone.utc).isoformat()
run_id = '2026-11-08-daily'
new_ids = []
for item in source['items']:
    if item['url'] not in urls:
        continue
    key = item['claim_key']
    prior = state['reported_items'].get(key, {})
    state['reported_items'][key] = {
        'post_id': item['id'], 'post_ids': [item['id']],
        'post_url': item['url'], 'claim_keys': [key],
        'first_report_date_beijing': prior.get('first_report_date_beijing', '2026-11-08'),
        'last_report_date_beijing': '2026-11-08',
        'reported_in_digest_at_utc': now,
        'digest_path': str(HERE / 'reddit_digest.md'),
        'source_record_path': str(HERE / 'reddit_sources.json'),
        'classification': item['classification'],
        'read_scope': item['read_scope'],
        'comments_status': item['comments_status'],
        'published_url': deployment['url'],
        'published_version_id': deployment['version_id'],
        'full_scan_complete': False,
    }
    new_ids.append(key)
assert len(new_ids) == 2
run = {
    'run_id': run_id, 'type': 'daily_heartbeat',
    'collection_cutoff_at_utc': proposal['cutoff_utc'],
    'artifact_saved_at_utc': now,
    'coverage_status': 'partial_public_access_two_selected_new_items',
    'complete_reddit_scan': False, 'reported_item_ids': new_ids,
    'digest_path': str(HERE / 'reddit_digest.md'),
    'source_record_path': str(HERE / 'reddit_sources.json'),
    'digest_sha256': hashlib.sha256((HERE / 'reddit_digest.md').read_bytes()).hexdigest(),
    'published_version_id': deployment['version_id'],
}
state['runs'] = [r for r in state['runs'] if r.get('run_id') != run_id] + [run]
state.update(last_run_id=run_id, last_successful_partial_read_at_utc=proposal['partial_check_at_utc'],
    last_attempt=run, last_attempt_at_utc=proposal['partial_check_at_utc'],
    last_attempt_report_date='2026-11-08', last_attempt_status='partial_read_published')
assert state['last_successful_check_at_utc'] == old['last_successful_check_at_utc']
tmp = state_path.with_suffix('.json.tmp')
save(tmp, state)
tmp.replace(state_path)
save(HERE / 'reddit_state_after.json', state)
save(HERE / 'reddit_publication.json', {'published_at': now, 'version_id': deployment['version_id'],
    'reported_claim_keys': new_ids, 'full_scan_complete': False,
    'prior_successful_full_check_timestamp_preserved': True,
    'fiNews_status': proposal['fiNews_status']})
print(json.dumps({'updated_claims': len(new_ids), 'full_scan_complete': False}, ensure_ascii=False))
