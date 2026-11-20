import UnityPy,pathlib
r=pathlib.Path(__file__).parent/'evidence/unpacked/assets/bin/Data'
e=UnityPy.load(str(r/'data.unity3d'),str(r/'sharedassets0.resource'))
for o in e.objects:
 if o.type.name=='AudioClip':
  d=o.read(); print(d.m_Name, d.m_Resource.m_Source,d.m_Resource.m_Offset,d.m_Resource.m_Size,d.m_Length, 'samples',list(d.samples.keys()))
  if d.m_Resource.m_Size:
   raw=(r/'sharedassets0.resource').read_bytes()[d.m_Resource.m_Offset:d.m_Resource.m_Offset+d.m_Resource.m_Size]
   out=r.parent.parent.parent.parent/'raw_audio';out.mkdir(exist_ok=True);(out/(d.m_Name+'.fsb')).write_bytes(raw)
