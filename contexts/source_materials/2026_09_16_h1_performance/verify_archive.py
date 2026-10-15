"""只读校验本次绩效资料归档的文件、哈希、来源覆盖与离线图片。"""
import hashlib
import json
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent
manifest = json.loads((root / 'manifest.json').read_text())
sources = json.loads((root / 'sources.json').read_text())
assets = json.loads((root / 'assets_manifest.json').read_text())
errors = []
for item in manifest:
    path = root / item['file']
    if not path.is_file():
        errors.append('缺少文件: ' + item['file'])
    elif hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
        errors.append('哈希不符: ' + item['file'])
urls = {item['url'] for item in sources}
for file in [root / 'weekly_evidence_notes.md', root.parent.parent / 'thought_review/2026_09_16_h1_okr_review.md']:
    for url in re.findall(r'https://docs\.xiaohongshu\.com/doc/[a-z0-9]+', file.read_text()):
        if url not in urls:
            errors.append('未归档引用来源: ' + url)
asset_urls = {item['url'] for item in assets if item['status'] == 'saved'}
for item in sources:
    path = root / item['file']
    if not path.is_file() or path.stat().st_size == 0:
        errors.append('来源无正文: ' + item['id'])
        continue
    if item.get('offline_file'):
        original = path.read_text()
        for url in re.findall(r'!\[[^\]]*\]\((https?://[^\s)]+)', original):
            if url not in asset_urls:
                errors.append('缺图片: ' + item['id'])
        expected = original
        for asset in assets:
            if asset['status'] == 'saved':
                expected = expected.replace(asset['url'], '../' + asset['file'])
        if (root / item['offline_file']).read_text() != expected:
            errors.append('离线版内容不符: ' + item['id'])
    elif '思考与复盘' not in path.read_text():
        errors.append('自评内容缺失: ' + item['id'])
for asset in assets:
    if asset['status'] != 'saved':
        errors.append('图片下载失败: ' + asset['url'])
    elif hashlib.sha256((root / asset['file']).read_bytes()).hexdigest() != asset['sha256']:
        errors.append('图片哈希不符: ' + asset['file'])
if errors:
    raise SystemExit('\n'.join(sorted(set(errors))))
print(f'校验通过：{len(sources)}份来源，{len(manifest)}个文件，{len(assets)}个图片链接。')
