from pathlib import Path
import json,textwrap,re,shutil
P=Path(__file__).resolve().parents[2]/'contexts/source_materials/anthropic_roadshow_2026_11_10';V=P/'verification'
(V/'fonts').mkdir(exist_ok=True);shutil.copy('/System/Library/Fonts/STHeiti Medium.ttc',V/'fonts/STHeiti Medium.ttc')
c=json.loads((P/'cues.json').read_text());z={}
for f in P.glob('zh_*.txt'):
 for line in f.read_text().splitlines():
  i,t=line.split('|',1);z[int(i)]=t

def tm(v):
 a=list(map(float,v.split(':')));sec=sum(x*60**i for i,x in enumerate(a[::-1]));cs=round(sec*100);return f'{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}'
def width(t):return sum(.55 if ord(ch)<128 else 1 for ch in t)
def zwrap(t):
 if width(t)<=39:return [t]
 choices=[]
 for i in range(1,len(t)):
  if t[i] in '，。；：！？、,.!?':continue
  penalty=abs(width(t[:i])-width(t)/2)
  if t[i-1] in '，。；：！？、 ':penalty-=3
  if t[i-1].isascii() and t[i].isascii() and t[i-1].isalnum() and t[i].isalnum():penalty+=100
  choices.append((penalty,i))
 i=min(choices)[1];return [t[:i].strip(),t[i:].strip()]
def esc(s):return s.replace('\\','\\\\').replace('{','（').replace('}','）')
head='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Bilingual,Heiti SC,42,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2.5,0.6,2,70,70,38,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
lines=[]
for x in c:
 a,b=x['time'].split(' --> ')
 zh='\\N'.join(map(esc,zwrap(z[x['id']])));en='\\N'.join(map(esc,textwrap.wrap(x['en'],width=98,break_long_words=False,break_on_hyphens=False)))
 lines.append(f"Dialogue: 0,{tm(a)},{tm(b)},Bilingual,,0,0,0,,{{\\fs42}}{zh}\\N{{\\fs32}}{en}")
(P/'anthropic_roadshow.bilingual.ass').write_text(head+'\n'.join(lines)+'\n')
print('ASS bilingual events',len(lines))
