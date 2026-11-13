from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess,json,re,bisect
P=Path(__file__).resolve().parents[2]/'contexts/source_materials/anthropic_roadshow_2026_11_10';V=P/'verification'
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',44)
cues=json.loads((P/'subtitle_validation.json').read_text())['cues']
srt=(P/'anthropic_roadshow.zh.srt').read_text(encoding='utf-8-sig');texts={int(b.splitlines()[0]):'\n'.join(b.splitlines()[2:]) for b in srt.strip().split('\n\n')}
checks=[]
for c in cues:
 t=texts[c['id']];im=Image.new('RGB',(1920,1080));d=ImageDraw.Draw(im);box=d.multiline_textbbox((0,0),t,font=font,spacing=8,stroke_width=2);w,h=box[2]-box[0],box[3]-box[1]
 checks.append({'id':c['id'],'width':w,'height':h,'fits_1920x1080_safe_area':w<=1728 and h<=216})
assert all(c['fits_1920x1080_safe_area'] for c in checks)
(V/'subtitle_layout.json').write_text(json.dumps({'renderer':'Pillow with STHeiti Medium 44 px; layout reference only, not a player screenshot','cue_count':len(checks),'checks':checks},ensure_ascii=False,indent=2))
times=[1,20,35,160,380,610,850,1110,1320,1550,1810,1840,1940,2080,2180,2300,2400,2493,2510,2550]
smallfont=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',20)
starts=[c['start'] for c in cues]
for page in range(2):
 sheet=Image.new('RGB',(1920,1550),'#eeeeee');sd=ImageDraw.Draw(sheet)
 for k,t in enumerate(times[page*10:(page+1)*10]):
  out=V/f'sample_{t:04d}.jpg';subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-threads','2','-ss',str(t),'-i',str(P/'anthropic_roadshow.mp4'),'-frames:v','1','-vf','scale=960:540','-y',str(out)],check=True)
  im=Image.open(out);i=bisect.bisect_right(starts,t)-1
  # Render a clearly labeled reference, not a native player capture.
  if i>=0 and t<cues[i]['end']:
   tx=texts[cues[i]['id']];d=ImageDraw.Draw(im);d.multiline_text((480,520),tx,font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',22),anchor='md',align='center',fill='white',stroke_width=2,stroke_fill='black',spacing=4)
  im.thumbnail((960,270));x=(k%2)*960;y=(k//2)*310;sheet.paste(im,(x,y));sd.text((x+8,y+272),f'{t//60:02d}:{t%60:02d}  字幕排版参考（非播放器截图）',font=smallfont,fill='black')
 sheet.save(V/f'contact_sheet_{page+1}.jpg',quality=88)
print('All 702 cue layouts fit; generated 20 sample-frame references')
