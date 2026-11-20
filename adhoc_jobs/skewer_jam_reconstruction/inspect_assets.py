import UnityPy,pathlib,json,collections
from UnityPy import config
config.USE_TYPETREE_BOOST=False
root=pathlib.Path(__file__).parent
files=[root/'evidence/unpacked/assets/bin/Data/data.unity3d']+sorted((root/'evidence/unpacked/assets/aa/Android').glob('*.bundle'))
rows=[]
for path in files:
 print('READ',path.name,flush=True)
 env=UnityPy.load(str(path))
 for o in env.objects:
  if o.type.name in ['Sprite','Texture2D','AudioClip','TextAsset','AnimationClip']:
   try:
    d=o.read();name=getattr(d,'m_Name','')
    row={'file':path.name,'id':o.path_id,'type':o.type.name,'name':name};rows.append(row)
    if o.type.name=='TextAsset':
     dest=root/'evidence/text';dest.mkdir(exist_ok=True);data=d.m_Script
     if isinstance(data,str):data=data.encode('utf-8','surrogateescape')
     (dest/(str(o.path_id)+'_'+name.replace('/','_')+'.txt')).write_bytes(data)
   except Exception as e:print('error',o.path_id,str(e)[:100],flush=True)
 (root/'evidence/unity_inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 print('ROWS',len(rows),flush=True)
