from pathlib import Path
import json, re, textwrap
ROOT=Path(__file__).resolve().parents[2]/'contexts/source_materials/anthropic_roadshow_2026_11_10'
cues=json.loads((ROOT/'cues.json').read_text())
zh={}
for p in ROOT.glob('zh_*.txt'):
    for line in p.read_text().splitlines():
        key,value=line.split('|',1)
        assert int(key) not in zh
        zh[int(key)]=value
assert set(zh)=={c['id'] for c in cues}
def time(t):
    if len(t.split(':'))==2: t='00:'+t
    return t.replace('.',',')
def seconds(t):
    return sum(float(v)*60**i for i,v in enumerate(re.split('[:,.]',t)[:-1][::-1]))+int(re.split('[,.]',t)[-1])/1000

def width(t): return sum(.55 if ord(ch)<128 else 1 for ch in t)
def wrap(t, limit=29):
    if width(t)<=limit:return t
    # Prefer natural punctuation or spaces near the middle; cap at two lines.
    middle=width(t)/2
    candidates=[]
    for i in range(1,len(t)):
        if t[i] in '，。、；：！？,.!?;:': continue
        penalty=abs(width(t[:i])-middle)
        if t[i-1] in '，。；：！？、 ':penalty-=3
        if t[i-1].isascii() and t[i].isascii() and t[i-1].isalnum() and t[i].isalnum():penalty+=100
        candidates.append((penalty,i))
    i=min(candidates)[1];return t[:i].strip()+'\n'+t[i:].strip()
checks=[]
for lang in ['zh','en','zh_en']:
    blocks=[]
    for c in cues:
        a,b=c['time'].split(' --> ');a,b=time(a),time(b)
        body=wrap(zh[c['id']]) if lang=='zh' else c['en'] if lang=='en' else wrap(zh[c['id']])+'\n'+c['en']
        blocks.append(f"{c['id']}\n{a} --> {b}\n{body}")
        if lang=='zh':
            assert seconds(b)>seconds(a)
            checks.append({'id':c['id'],'start':seconds(a),'end':seconds(b),'cps':round(len(zh[c['id']])/(seconds(b)-seconds(a)),2),'max_line_width':max(map(width,body.splitlines()))})
    (ROOT/f'anthropic_roadshow.{lang}.srt').write_text('\n\n'.join(blocks)+'\n',encoding='utf-8-sig')
(ROOT/'anthropic_roadshow.srt').write_bytes((ROOT/'anthropic_roadshow.zh.srt').read_bytes())
(ROOT/'subtitle_validation.json').write_text(json.dumps({'cue_count':len(cues),'missing':[],'max_cps':max(x['cps'] for x in checks),'max_line_width':max(x['max_line_width'] for x in checks),'cues':checks},ensure_ascii=False,indent=2))
print('Built Chinese, English and bilingual SRT:',len(cues),'cues; max CPS',max(x['cps'] for x in checks))
