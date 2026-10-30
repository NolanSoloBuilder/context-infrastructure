"""Read-only security-search checks for the three unresolved companies."""
import json
import time
import xml.etree.ElementTree as ET
from ui import OUT, adb, snapshot
from manage import click, find

def query(term):
    root = snapshot()
    if find(root, rid='action_search'):
        root = click(root, rid='action_search')
    root = click(root, rid='search_input_text')
    if find(root, rid='action_delete_text'):
        root = click(root, rid='action_delete_text')
    for c in term:
        assert c.isascii() and c.isalnum()
        adb('shell', 'input', 'text', c)
        time.sleep(.14)
    root = snapshot()
    assert find(root, rid='search_input_text', text=term)
    root = click(root, rid='search_btn')
    tabs = find(root, rid='title_text', text='股票')
    if len(tabs) == 1:
        root = click(root, rid='title_text', text='股票')
    parents = {c: p for p in root.iter() for c in p}
    securities = []
    for code in [n for n in root.iter('node') if n.get('resource-id', '').split(':id/')[-1] in ('stock_code_tv', 'stockCode')]:
        card = code
        names = []
        while card in parents and not names:
            card = parents[card]
            names = [n for n in card.iter('node') if n.get('resource-id', '').split(':id/')[-1] in ('stock_name_tv', 'stockName')]
        if len(names) == 1:
            tags = [n.get('text') for n in card.iter('node') if n.get('resource-id', '').endswith('/stock_tag')]
            securities.append({'name': names[0].get('text'), 'code': code.get('text'), 'tags': tags})
    (OUT / ('availability_' + term + '.xml')).write_bytes(ET.tostring(root, encoding='utf-8'))
    result = {'query': term, 'visible_stock_results': securities, 'scope': '雪球股票搜索当前可见结果，未选择不匹配证券，也不是全市场不支持声明'}
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result

if __name__ == '__main__':
    results = [query(term) for term in ('Galbot', 'Samsung', '005930', 'SKHynix', '000660')]
    (OUT / 'availability_checks.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
