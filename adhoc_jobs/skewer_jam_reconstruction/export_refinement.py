from pathlib import Path
from PIL import Image,ImageDraw
import UnityPy,json,math
root=Path(__file__).parent;out=root/'evidence/refinement';out.mkdir(exist_ok=True)
names={'lock','ui_title_lock','btn_booster','btn_booster_lock','kitchen_order','box_score_ic_home 1','ic_add_order','HUD_icon_star','icon_hand1','icon_hand2','fr_tut_01','fr_tut_02','fr_hint_normal','arrow_tutorial','icon_CheckMark','star','Star01','Additive_Star3','Effects-color_spark','flare01','glow_','cloud_2x2_soft_0','btn_brown','btn_green','box_title_blue','ui_title_popup','fr_timer','sound_on','sound_off','muson','musoff','vibration_on','vibration_off','ui_time','ui_bar_u','ui_bar_green'}
e=UnityPy.load(str(root/'evidence/unpacked/assets/bin/Data/data.unity3d'));rows=[]
for o in e.objects:
 if o.type.name!='Sprite':continue
 d=o.read()
 if d.m_Name not in names and not d.m_Name.startswith(('ic_','HUD_','o_','ui_opfeature','ui_box','icon_','fr_prg','prg_','ui_title_ic')):continue
 fn=str(o.path_id)+'_'+d.m_Name.replace(' ','_')+'.png';im=d.image;im.save(out/fn);rows.append({'name':d.m_Name,'id':o.path_id,'file':fn,'size':im.size})
(out/'manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
cols=7;w=140;h=145;sheet=Image.new('RGB',(cols*w,math.ceil(len(rows)/cols)*h),'#f0dfc0');draw=ImageDraw.Draw(sheet)
for i,r in enumerate(rows):
 im=Image.open(out/r['file']);im.thumbnail((125,100));x=i%cols*w;y=i//cols*h;sheet.paste(im,(x+(w-im.width)//2,y),im);draw.text((x+3,y+103),r['name'][:24],fill='#3e2617');draw.text((x+3,y+118),str(r['id'])+' '+str(r['size']),fill='#3e2617')
sheet.save(out/'sheet.jpg')
im=Image.open(root/'evidence/reference_refine.png');im.thumbnail((360,800));im.save(root/'evidence/reference_refine_small.png')
print('exported',len(rows))
