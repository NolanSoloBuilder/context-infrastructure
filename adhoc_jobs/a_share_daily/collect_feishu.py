"""Read authorized group cards via CLI, retaining author-only review candidates.

Generic message GET avoids the shortcut's optional contacts/name enrichment.
Candidates remain private and require review before inclusion in a report.
"""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def text_nodes(value):
    if isinstance(value, list):
        for item in value:
            yield from text_nodes(item)
    elif isinstance(value, dict):
        if value.get('tag') == 'text' and isinstance(value.get('text'), str):
            yield value['text']
        else:
            for child in value.values():
                if isinstance(child, (list, dict)):
                    yield from text_nodes(child)


def author_candidate(message, config):
    if message.get('deleted') or message.get('msg_type') != 'interactive':
        return None
    if message.get('sender', {}).get('id') != config['sync_sender_app_id']:
        return None
    card = json.loads(message['body']['content'])
    title = card.get('title', '')
    match = re.fullmatch(r'📢 (回答|新动态) · (\d{4}-\d{2}-\d{2} \d{2}:\d{2})', title)
    if not match:
        return None
    nodes = list(text_nodes(card.get('elements', [])))
    if match[1] == '回答':
        # Structural card boundary, not a guess based on words in the question.
        boundaries = [i for i, text in enumerate(nodes) if text.strip() == '星主回答']
        if len(boundaries) != 1:
            return None
        nodes = nodes[boundaries[0] + 1:]
    body = '\n\n'.join(nodes).strip()
    # Quoted questions can occur inside an author's answer. Exclude those too.
    body = '\n'.join(line for line in body.splitlines() if not line.lstrip().startswith('>')).strip()
    if not body:
        return None
    return {'message_id': message['message_id'], 'kind': match[1],
            'source_time': match[2] + '+08:00', 'sync_create_time': message.get('create_time'),
            'sync_update_time': message.get('update_time'),
            'content_sha256': hashlib.sha256(body.encode()).hexdigest(),
            'author_text': body, 'review_required': True,
            'provenance': '群内机器人标记的星主回答/新动态；非原星球直读'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', required=True)
    parser.add_argument('--end', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads((ROOT/'contexts/survey_sessions/a_share_daily/feishu_source.json').read_text())
    start, end = (datetime.fromisoformat(v) for v in (args.start, args.end))
    assert start.tzinfo and end.tzinfo and start < end
    params = {'container_id_type': 'chat', 'container_id': config['chat_id'],
              'start_time': str(int(start.timestamp())), 'end_time': str(int(end.timestamp())),
              'sort_type': 'ByCreateTimeDesc', 'page_size': 50}
    candidates, seen_ids, page_tokens = [], set(), set()
    pages = count = 0
    while True:
        result = subprocess.run(['lark-cli', '--profile', config['profile'], 'api', 'GET',
            '/open-apis/im/v1/messages', '--as', 'user', '--params', json.dumps(params)],
            capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stdout or result.stderr)
        response = json.loads(result.stdout)
        if response.get('code') != 0:
            raise RuntimeError(f"Message API failed: {response.get('code')} {response.get('msg')}")
        data = response['data']
        pages += 1
        for message in data.get('items', []):
            if message['message_id'] in seen_ids:
                continue
            seen_ids.add(message['message_id'])
            count += 1
            candidate = author_candidate(message, config)
            if candidate:
                candidates.append(candidate)
        if not data.get('has_more'):
            break
        token = data.get('page_token')
        if not token or token in page_tokens or pages >= 20:
            raise RuntimeError('Incomplete pagination; do not advance the report watermark')
        page_tokens.add(token)
        params['page_token'] = token
    payload = {'window_start': args.start, 'window_end': args.end, 'chat_name': config['chat_name'],
               'message_count': count, 'pages': pages, 'complete_api_window': True,
               'original_source_completeness': '未知，群同步可能有缺漏', 'candidates': candidates}
    fd = os.open(args.out, os.O_WRONLY|os.O_CREAT|os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
    print(json.dumps({'messages': count, 'author_candidates': len(candidates), 'pages': pages,
                      'private_review_file': str(args.out)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
