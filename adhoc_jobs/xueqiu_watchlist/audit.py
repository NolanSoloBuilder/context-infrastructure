"""Read back each custom watchlist group from the Android app itself."""
import json
import re
import xml.etree.ElementTree as ET
from ui import OUT, adb, snapshot, tap_node
from manage import find

def nums(node):
    return list(map(int, re.findall(r'\d+', node.get('bounds'))))

def home():
    root = snapshot()
    for _ in range(50):
        if find(root, rid='main_tab_host'):
            return root
        assert any(n.get('package') == 'com.xueqiu.android' for n in root.iter('node')), 'Stop outside the authorized app'
        adb('shell', 'input', 'keyevent', '4')
        root = snapshot()
    raise RuntimeError('Could not return to main watchlist')

def select_group(root, target):
    direction = 'left'
    seen = None
    for _ in range(9):
        indicators = find(root, rid='indicator')
        assert len(indicators) == 1
        node = indicators[0]
        x1, y1, x2, y2 = nums(node)
        names = [n for n in node.iter('node') if n.get('text')]
        matches = [n for n in names if n.get('text') == target and nums(n)[2] - nums(n)[0] > 25]
        if matches:
            assert len(matches) == 1
            tap_node(matches[0])
            return snapshot()
        signature = [(n.get('text'), n.get('bounds')) for n in names]
        if signature == seen:
            direction = 'right' if direction == 'left' else 'left'
        seen = signature
        start, end = (x2 - 50, x1 + 50) if direction == 'left' else (x1 + 50, x2 - 50)
        adb('shell', 'input', 'swipe', str(start), str((y1+y2)//2), str(end), str((y1+y2)//2), '400')
        root = snapshot()
    raise RuntimeError('Group not found in main tabs: ' + target)

if __name__ == '__main__':
    plan = json.loads((OUT / 'plan.json').read_text())
    result = {}
    root = home()
    for i, (name, expected) in enumerate(plan['groups'].items(), 1):
        root = select_group(root, name)
        codes = [n.get('text') for n in find(root, rid='portfolio_stockCode')]
        if set(codes) != set(expected):
            root = snapshot()
            codes = [n.get('text') for n in find(root, rid='portfolio_stockCode')]
        assert set(codes) == set(expected), (name, expected, codes)
        file = 'group_' + str(i)
        (OUT / (file + '.png')).write_bytes(adb('exec-out', 'screencap', '-p'))
        (OUT / (file + '.xml')).write_bytes(ET.tostring(root, encoding='utf-8'))
        result[name] = {'codes_read_back': codes, 'screenshot': file + '.png', 'verified': True}
        print(json.dumps({name: codes}, ensure_ascii=False), flush=True)
    (OUT / 'final_audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
