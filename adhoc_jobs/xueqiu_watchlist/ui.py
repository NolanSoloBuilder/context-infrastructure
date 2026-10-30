"""Small, UI-only Android helper for the authorized Xueqiu watchlist task."""
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ADB = '/Users/xuhao/Library/Android/sdk/platform-tools/adb'
DEVICE = 'a78e52ce'
OUT = Path('/Users/xuhao/Documents/Other/context-infrastructure/contexts/survey_sessions/us_market_daily/2026-10-28/xueqiu_watchlist')
OUT.mkdir(parents=True, exist_ok=True)

def adb(*args):
    return subprocess.check_output([ADB, '-s', DEVICE, *args])

def snapshot():
    adb('shell', 'uiautomator', 'dump', '/sdcard/xueqiu_window.xml')
    data = adb('shell', 'cat', '/sdcard/xueqiu_window.xml')
    (OUT / 'current.xml').write_bytes(data)
    root = ET.fromstring(data)
    return root

def show(root):
    for node in root.iter('node'):
        a = node.attrib
        if a.get('text') or a.get('content-desc') or a.get('class') == 'android.widget.EditText' or (a.get('clickable') == 'true' and a.get('resource-id')):
            print(json.dumps([a.get('text') or a.get('content-desc'), a.get('resource-id', '').split(':id/')[-1], a.get('bounds'), 'checked' if a.get('checked') == 'true' else ''], ensure_ascii=False))

def tap_node(node):
    xy = list(map(int, re.findall(r'\d+', node.attrib['bounds'])))
    adb('shell', 'input', 'tap', str((xy[0] + xy[2]) // 2), str((xy[1] + xy[3]) // 2))

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'show'
    if cmd in ('text', 'id'):
        root = snapshot()
        value = sys.argv[2]
        key = 'text' if cmd == 'text' else 'resource-id'
        matches = [n for n in root.iter('node') if n.attrib.get(key) == value]
        if len(matches) != 1:
            raise RuntimeError(f'Expected one visible {key}={value}, got {len(matches)}')
        tap_node(matches[0])
    elif cmd == 'input':
        value = sys.argv[2]
        if not re.fullmatch(r'[A-Za-z0-9_. -]+', value):
            raise RuntimeError('Only literal safe ASCII typing is supported')
        adb('shell', 'input', 'text', value.replace(' ', '%s'))
    elif cmd == 'key':
        if sys.argv[2] not in ('4', '66', '67', '123'):
            raise RuntimeError('Unexpected key')
        adb('shell', 'input', 'keyevent', sys.argv[2])
    elif cmd == 'shot':
        name = sys.argv[2]
        if not re.fullmatch(r'[a-z0-9_-]+', name):
            raise RuntimeError('Invalid screenshot name')
        target = OUT / (name + '.png')
        target.write_bytes(adb('exec-out', 'screencap', '-p'))
        print(target)
        sys.exit(0)
    elif cmd != 'show':
        raise RuntimeError('Unsupported command')
    show(snapshot())
