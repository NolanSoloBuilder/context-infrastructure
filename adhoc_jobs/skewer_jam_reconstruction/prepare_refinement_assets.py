from pathlib import Path
from PIL import Image,ImageDraw
import UnityPy,json,hashlib
root=Path(__file__).parent;target=Path('/Users/xuhao/Documents/Other/xhs-minitools/packages/skewer-jam/src/assets');evidence=root/'evidence/refinement';manifest=json.loads((evidence/'manifest.json').read_text());provenance=[]
selected={'icon_arrow_turn_l':'undo_icon','icon_Plus':'plus_icon','ic_OnlineBonus':'orders_icon','lock':'lock','ui_title_lock':'lock_label','icon_hand1':'tutorial_hand','arrow_tutorial':'tutorial_arrow','flare01':'fx_flare','Additive_Star3':'fx_star','Star01':'fx_confetti','ic_setting':'settings_icon','icon_CheckMark':'check','HUD_icon_star':'star_icon','ic_close':'close','vibration_on':'vibration_on','vibration_off':'vibration_off'}
for name,out in selected.items():
 r=next(x for x in manifest if x['name']==name);src=evidence/r['file'];Image.open(src).save(target/(out+'.webp'),'WEBP',lossless=True,method=6);provenance.append({'asset':out+'.webp','source':'data.unity3d','id':r['id'],'original_name':name,'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
# Preserve fine linework and alpha edges of extracted food and tray sprites.
for item in json.loads((root/'evidence/asset_provenance.json').read_text()):
 if item['asset'].startswith('food_') or any(tag in item['asset'] for tag in ['grill','sold','order','slot']):
  im=Image.open(root/item['original']['file']);im.thumbnail((400,400));im.save(target/item['asset'],'WEBP',lossless=True,method=6)
rows=[]
for theme,filename,suffix in [('sakura','theme_kr_','Korea'),('japan','theme_jp_','JP'),('china','theme_cn_','China')]:
 path=next((root/'evidence/unpacked/assets/aa/Android').glob(filename+'assets*'));env=UnityPy.load(str(path));want={'ic_squareplate_'+suffix:theme+'_preview','ic_order01_'+suffix+'_2':theme+'_addorder'}
 for o in env.objects:
  if o.type.name!='Sprite':continue
  d=o.read()
  if d.m_Name not in want:continue
  out=want[d.m_Name];im=d.image;im.save(target/(out+'.webp'),'WEBP',lossless=True,method=6);rows.append((out,im));provenance.append({'asset':out+'.webp','source':path.name,'id':o.path_id,'original_name':d.m_Name})
sheet=Image.new('RGB',(len(rows)*120,135),'#efdfc0');draw=ImageDraw.Draw(sheet)
for i,(name,im) in enumerate(rows):
 im.thumbnail((110,95));sheet.paste(im,(i*120,0),im);draw.text((i*120,98),name,fill='black')
sheet.save(evidence/'theme_hud.jpg');(evidence/'web_assets.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2));print('new sprites',len(provenance))
