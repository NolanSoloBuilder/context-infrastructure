from PIL import Image,ImageDraw
import pathlib,json,math
root=pathlib.Path(__file__).parent
m=json.loads((root/'evidence/exported/manifest.json').read_text())
for group in ['food','decor']:
 rows=[r for r in m if r['type']=='Sprite' and ((r['name'].startswith('item_') and r['source'].startswith('shared_ui')) if group=='food' else not r['name'].startswith('item_'))]
 rows=sorted(rows,key=lambda r:(r['name'],r['source']))
 if group=='food':rows=rows[:100]
 cols=8;w=128;h=140;sheet=Image.new('RGB',(cols*w,math.ceil(len(rows)/cols)*h),'#eee2ca');draw=ImageDraw.Draw(sheet)
 for i,r in enumerate(rows):
  im=Image.open(root/r['file']);im.thumbnail((110,100));x=i%cols*w;y=i//cols*h;sheet.paste(im,(x+(w-im.width)//2,y),im);draw.text((x+4,y+102),r['name'][:23],fill='black');draw.text((x+4,y+116),r['file'].split('/')[-2]+'/'+str(r['id'])[:12],fill='black')
 sheet.save(root/('evidence/'+group+'_sheet.jpg'))
