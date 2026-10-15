import json,base64,io
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).parent
raw=json.load(open('/tmp/cited-alpha-cross-source-business-02/recovered-provider-readonly/providerDocuments.json'))
for p in (4,5,7,8):
 page=next(pg for d in raw for pg in d['pages'] if int(pg['pageNumber'])==p)
 im=Image.open(io.BytesIO(base64.b64decode(page['image']['content']))).convert('RGB');draw=ImageDraw.Draw(im)
 fields=json.loads((root/f'page-{p}.json').read_text())['fields']
 for f in fields:
  b=f['bbox'] or {};vs=b.get('normalized_vertices',[])
  if vs:
   coords=[(v['x']*im.width,v['y']*im.height) for v in vs];draw.line(coords+[coords[0]],fill='red',width=2)
 im.thumbnail((1333,750));im.save(root/f'page-{p}-all-original-polygons.png')
