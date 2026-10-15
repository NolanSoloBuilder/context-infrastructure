"""Independent adversarial image checks; synthetic fixtures, no service/cloud IO."""
import sys,io,base64,hashlib,importlib.util,json
from pathlib import Path
from copy import deepcopy
sys.path.insert(0,'/Users/xuhao/Documents/Other/mindspace_ml_backend')
from PIL import Image
from mindspace.service.research_agent.page_rendition import retained_page_rendition
s=importlib.util.spec_from_file_location('backend_checked','/Users/xuhao/Documents/Other/mindspace_backend/mindspace/service/ml_service/research_page_rendition.py');backend=importlib.util.module_from_spec(s);s.loader.exec_module(backend)
version={'parserVersion':'research-document-layout-normalizer/v1','documentVersionId':'offline-image-negative','rawReceipt':{'sha256':'a'*64},'providerReceipt':{'sha256':'b'*64}}
record={'line_id':'l','page_number':1,'bbox':{'normalized_vertices':[{'x':.1,'y':.1},{'x':.2,'y':.1},{'x':.2,'y':.2},{'x':.1,'y':.2}]}}
locator={'kind':'line','id':'l'}
results=[]
def image(orientation):
 im=Image.new('RGB',(40,20),'white');buf=io.BytesIO();kwargs={}
 if orientation is not None:
  exif=Image.Exif();exif[274]=orientation;kwargs['exif']=exif
 im.save(buf,format='JPEG',**kwargs);return buf.getvalue()
def page(raw):return {'pageNumber':1,'dimension':{'width':40,'height':20,'unit':'pixels'},'image':{'width':40,'height':20,'mimeType':'image/jpeg','content':base64.b64encode(raw).decode()}}
def call(p):return retained_page_rendition(version=version,provider_documents=[{'pages':[p]}],record=record,locator=locator)
def rejects(fn):
 try:fn()
 except ValueError:return True
 return False
for orientation in [None,1,2,3,6,8]:
 raw=image(orientation);p=page(raw)
 # Backend standalone negative is not masked by ML's earlier rejection.
 metadata={'schemaVersion':'research-page-rendition/v1','surface':'retained_provider_page','documentVersionId':version['documentVersionId'],'rawSha256':'a'*64,'providerSha256':'b'*64,'fieldKind':'line','fieldId':'l','pageNumber':1,'mimeType':'image/jpeg','byteSize':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'width':40,'height':20,'locationPrecision':'field','bboxNormalized':{'x':.1,'y':.1,'width':.1,'height':.1}}
 backend.validate_page_rendition(metadata,version=version,locator=locator,page_number=1)
 ml_rejected=rejects(lambda:call(p));b_rejected=rejects(lambda:backend.decode_page_image(base64.b64encode(raw).decode(),metadata))
 expect=orientation not in (None,1)
 results.append({'case':'exif','orientation':orientation,'mlRejected':ml_rejected,'backendRejected':b_rejected,'pass':ml_rejected==expect and b_rejected==expect})
for label,change in [('non-pixels',lambda p:p['dimension'].update(unit='points')),('width-mismatch',lambda p:p['dimension'].update(width=41)),('height-mismatch',lambda p:p['dimension'].update(height=21)),('missing-dimension',lambda p:p.pop('dimension'))]:
 p=page(image(None));change(p);rejected=rejects(lambda:call(p));results.append({'case':label,'mlRejected':rejected,'pass':rejected})
Path('/tmp/cited-alpha-page-rendition-cross-review/final-negative-result.json').write_text(json.dumps(results,indent=2))
print(json.dumps({'cases':len(results),'passed':sum(r['pass'] for r in results),'results':results}))
assert all(r['pass'] for r in results)
