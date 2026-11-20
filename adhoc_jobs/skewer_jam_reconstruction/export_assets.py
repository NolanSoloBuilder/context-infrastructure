import UnityPy,pathlib,json,re
from UnityPy.helpers import TypeTreeHelper
TypeTreeHelper.read_typetree_boost=None
root=pathlib.Path(__file__).parent;out=root/'evidence/exported';out.mkdir(exist_ok=True)
files=[root/'evidence/unpacked/assets/bin/Data/data.unity3d']+sorted((root/'evidence/unpacked/assets/aa/Android').glob('*.bundle'))
manifest=[]
for i,path in enumerate(files):
 env=UnityPy.load(str(path));folder=out/str(i);folder.mkdir(exist_ok=True)
 for obj in env.objects:
  if obj.type.name not in ['Sprite','AudioClip','AnimationClip']:continue
  try:
   d=obj.read();name=d.m_Name
   if obj.type.name=='Sprite':
    if not (re.match(r'item_\d+',name) or re.search(r'grill|plate|^BG_|^bg$|^bg[23]$|order0|^xien|ic_pause|sound_|muson|musoff|magnet|shuffle|hammer|booster|pattern_bg_head|sold',name,re.I)):continue
    p=folder/(str(obj.path_id)+'_'+re.sub(r'[^\w -]','_',name)+'.png');d.image.save(p)
    manifest.append({'name':name,'source':path.name,'file':str(p.relative_to(root)),'id':obj.path_id,'type':'Sprite'})
   elif obj.type.name=='AudioClip' and i==0:
    for key,data in d.samples.items():
     p=folder/(re.sub(r'[^\w .-]','_',name)+'_'+key);p.write_bytes(data)
     manifest.append({'name':name,'file':str(p.relative_to(root)),'type':'AudioClip'})
   elif obj.type.name=='AnimationClip' and i==0:
    (folder/(name+'.json')).write_text(json.dumps(obj.read_typetree(),default=str))
  except Exception as e:print('ERR',name,str(e)[:120],flush=True)
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(path.name,len(manifest),flush=True)
