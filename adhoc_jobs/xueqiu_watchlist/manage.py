"""Assign explicitly requested securities using observed Xueqiu UI controls only."""
import datetime
import json
import sys
import time
import xml.etree.ElementTree as ET
from ui import OUT, adb, snapshot, tap_node

P = 'com.xueqiu.android:id/'

def title_code(expected):
    return expected[2:] if expected.startswith(('SH', 'SZ')) else expected

def find(root, *, text=None, rid=None):
    return [n for n in root.iter('node') if (text is None or n.get('text') == text) and (rid is None or n.get('resource-id') == P + rid)]

def click(root, **selector):
    nodes = find(root, **selector)
    assert len(nodes) == 1, (selector, len(nodes))
    tap_node(nodes[0])
    return snapshot()

def save_xml(root, name):
    (OUT / (name + '.xml')).write_bytes(ET.tostring(root, encoding='utf-8'))

def record(item):
    target = OUT / 'operations.json'
    items = json.loads(target.read_text()) if target.exists() else []
    item['recorded_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    items.append(item)
    target.write_text(json.dumps(items, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(item, ensure_ascii=False), flush=True)

def search_detail(query, expected_code):
    root = click(snapshot(), rid='action_search')
    root = click(root, rid='search_input_text')
    if find(root, rid='action_delete_text'):
        root = click(root, rid='action_delete_text')
    for c in query:
        assert c.isascii() and (c.isalnum() or c in '.-')
        adb('shell', 'input', 'text', c)
        time.sleep(.14)
    root = snapshot()
    assert find(root, rid='search_input_text', text=query), 'Search text must match before submission'
    root = click(root, rid='search_btn')
    codes = find(root, rid='stock_code_tv', text=expected_code)
    if not codes:
        save_xml(root, 'search_missing_' + query)
        raise RuntimeError('Exact security not found: ' + expected_code)
    assert len(codes) == 1
    parents = {c: p for p in root.iter() for c in p}
    card = codes[0]
    names = []
    while card in parents and not names:
        card = parents[card]
        names = find(card, rid='stock_name_tv')
    assert len(names) == 1, 'One matching stock card is required'
    name = names[0].get('text')
    tap_node(names[0])
    root = snapshot()
    symbols = find(root, rid='title_bar_symbol')
    assert len(symbols) == 1 and symbols[0].get('text') == title_code(expected_code), (name, [n.get('text') for n in symbols])
    print(json.dumps({'detail': name, 'code': expected_code}, ensure_ascii=False), flush=True)
    return root, name

def groups(root):
    parents = {c: p for p in root.iter() for c in p}
    result = {}
    for n in find(root, rid='nesting_portfolio_selection_item_name'):
        boxes = [b for b in parents[n].iter('node') if b.get('checkable') == 'true']
        assert len(boxes) == 1
        result[n.get('text')] = boxes[0]
    return result

def group_dialog(root):
    root = click(root, text='设自选')
    for _ in range(3):
        if find(root, text='修改分组'):
            break
        root = snapshot()
    root = click(root, text='修改分组')
    for _ in range(3):
        if find(root, text='选择分组'):
            break
        root = snapshot()
    return root

def assign_detail(expected_code, target, resume_new=False):
    root = snapshot()
    assert resume_new or find(root, rid='title_bar_symbol', text=title_code(expected_code))
    existing = not resume_new and bool(find(root, text='设自选'))
    if resume_new:
        assert find(root, text='选择分组')
    elif existing:
        root = group_dialog(root)
    else:
        assert find(root, text='加自选'), 'Unexpected watchlist control; never touch trade controls'
        root = click(root, text='加自选')
        for _ in range(3):
            if find(root, text='选择分组') or find(root, text='设自选'):
                break
            root = snapshot()
        save_xml(root, 'after_add_' + expected_code)
        if not find(root, text='选择分组'):
            assert find(root, text='设自选'), 'New addition outcome needs inspection'
            root = group_dialog(root)
    before = {name: box.get('checked') == 'true' for name, box in groups(root).items()}
    assert target in before
    if not before[target]:
        tap_node(groups(root)[target])
        root = snapshot()
    assert groups(root)[target].get('checked') == 'true'
    for name, checked in before.items():
        if name != target:
            assert (groups(root)[name].get('checked') == 'true') == checked, 'Preserve other memberships'
    root = click(root, text='确认')
    for _ in range(3):
        if find(root, rid='tv_dialog_title', text='相关活跃用户'):
            root = click(root, rid='iv_close')
        if find(root, text='设自选'):
            break
        root = snapshot()
    root = group_dialog(root)
    after = {name: box.get('checked') == 'true' for name, box in groups(root).items()}
    assert after[target] and all(after[n] == v for n, v in before.items() if n != target and n != '全部')
    save_xml(root, 'verified_' + expected_code)
    record({'code': expected_code, 'group': target, 'previously_in_watchlist': existing, 'verified_groups': [n for n, v in after.items() if v], 'status': 'saved_and_reopened_verified'})
    return click(root, rid='head_left_close_iv')

if __name__ == '__main__':
    if sys.argv[1] == 'assign':
        assign_detail(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'search':
        root, name = search_detail(sys.argv[2], sys.argv[3])
        print('Opened: ' + name)
    else:
        raise RuntimeError('Unknown operation')
