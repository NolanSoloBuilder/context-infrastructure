from pathlib import Path
from PIL import Image
import json,subprocess,hashlib
root=Path(__file__).parent;target=Path('/Users/xuhao/Documents/Other/xhs-minitools/packages/skewer-jam/src/assets')
m=json.loads((root/'evidence/exported/manifest.json').read_text());provenance=[]
# Selected ordinary-food atlas entries; distinct holiday variants share names.
ids=[-832669746503221095,-8440009507723762016,1173278703428013569,673055358020661677,2658414185827372375,-3095080633034963091]
# Add unambiguous ordinary foods from the base atlas.
for name in ['item_010','item_022','item_039','item_046','item_050','item_052','item_049','item_047','item_048']:
 choices=[r for r in m if r['name']==name and r['source'].startswith('shared_ui')]
 # Select specific normal-set entries from observed atlas.
 overrides={'item_010':-4697387746039997460,'item_022':1254037844690012011,'item_039':-1254212696618313419,'item_046':-8134268147501604000}
 ids.append(next((r['id'] for r in choices if str(r['id']).startswith(str(overrides.get(name,''))[:8])),choices[0]['id']))
selected=[]
for i,pid in enumerate(ids):
 r=next(r for r in m if r.get('id')==pid);selected.append((r,'food_'+str(i)))
for theme,folder in [('sakura','7'),('japan','6'),('china','5')]:
 names={'sakura':{'wall':'BG_Korea','shelf':'BG_Korea_2','grill':'ui_grill_Korea','sold':'ui_grill_Korea_2','order':'ic_order01_Korea','slot':'ic_squareplate02_Korea'},'japan':{'wall':'BG_Japan','shelf':'BG_JP_2','grill':'ui_grill_JP-1','sold':'ui_grill_JP','order':'ic_order01_JP','slot':'ic_squareplate02_JP'},'china':{'wall':'BG_China','shelf':'BG_China2','grill':'ui_grill_China-1','sold':'ui_grill_China','order':'ic_order01_China','slot':'ic_squareplate02_China'}}[theme]
 for key,name in names.items():selected.append((next(r for r in m if r['name']==name and r['file'].split('/')[-2]==folder),theme+'_'+key))
for name in ['ic_pause','magnet','shuffle','hammer','icon_booster_magicwand','booster_plus','btn_booster','btn_booster_lock','sound_on','sound_off','muson','musoff']:
 selected.append((next(r for r in m if r['name']==name and r['file'].split('/')[-2]=='0'),name))
for r,name in selected:
 im=Image.open(root/r['file']);im.thumbnail((768,768) if name.endswith('wall') else (400,400));out=target/(name+'.webp');im.save(out,'WEBP',quality=88,method=6)
 provenance.append({'asset':out.name,'original':r,'sha256':hashlib.sha256((root/r['file']).read_bytes()).hexdigest()})
# Audio has its own reproducible quality-preserving build.
subprocess.run(['python3',str(root/'prepare_audio_assets.py')],check=True)
(root/'evidence/asset_provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2))
print('images',len(selected))
