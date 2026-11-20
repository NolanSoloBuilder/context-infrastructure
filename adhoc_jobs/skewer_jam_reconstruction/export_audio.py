import UnityPy,pathlib
root=pathlib.Path(__file__).parent;r=root/'evidence/unpacked/assets/bin/Data';out=root/'evidence/audio';out.mkdir(exist_ok=True)
e=UnityPy.load(str(r/'data.unity3d'),str(r/'sharedassets0.resource'))
for o in e.objects:
 if o.type.name=='AudioClip':
  d=o.read()
  for name,data in d.samples.items():(out/name).write_bytes(data)
print('WAV',len(list(out.glob('*.wav'))))
