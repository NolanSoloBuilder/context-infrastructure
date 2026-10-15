import sys,json,copy,hashlib
from pathlib import Path
sys.path.insert(0,'/Users/xuhao/Documents/Other/mindspace_ml_backend')
from mindspace.service.document_ai.layout_parse_adapter import DocumentAILayoutParseAdapter
from mindspace.service.research_agent.immutable_document_tools import ImmutableDocumentResearchTools
from page_view import overview,wire
root=Path(__file__).parent
raw=json.loads(Path('/tmp/cited-alpha-cross-source-business-02/recovered-provider-readonly/providerDocuments.json').read_text())
n=DocumentAILayoutParseAdapter().to_parse_result(document_ai_documents=raw,document_id='doc_file_e9aca68920734fabbc3a27b72d27cfa3',source='conversation_upload',parse_run_id='offline-existing-provider').model_dump(mode='json')
version='offline-material-sha-'+hashlib.sha256(wire(n)).hexdigest()
# Use existing production _rows exact kind/ID resolution, without invoking IO/auth or making evidence.
tool=object.__new__(ImmutableDocumentResearchTools)
lookup={(k,i):r for k,i,r in tool._rows(n)}
results={}
for page in [4,5,7,8]:
 first32=overview(n,version_id=version,page=page)
 view=overview(n,version_id=version,page=page,max_bytes=49152)
 assert view['coverage']['complete'] and not view['truncated']
 for f in view['fields']:
  original=lookup[f['kind'],f['id']]
  assert f['text']==original['text'] and f['bbox']==original.get('bbox')
 assert len(view['fields'])==len([r for r in n['lines'] if r['page_number']==page and r['text'].strip()])
 (root/f'page-{page}.json').write_bytes(wire(view))
 results[page]={'bytes':len(wire(view)),'under32KiB':first32['coverage']['complete'],'fieldsAt32KiB':len(first32['fields']),'fields':len(view['fields']),'coverage':view['coverage'],'availableLayers':view['availableLayers']}
 # All pagination recovers exactly full view, with full text and original coordinates.
 got=[];cursor=None
 while True:
  part=overview(n,version_id=version,page=page,cursor=cursor,max_bytes=4000,max_fields=7)
  assert len(wire(part))<=4000
  got+=part['fields'];cursor=part['nextCursor']
  if cursor is None:break
 assert got==view['fields']
 spans=overview(n,version_id=version,page=page,kind='span',max_bytes=65536)
 assert spans['availableLayers']['span']>0
# Cross-scope/version/material/kind rejects cursor.
c=overview(n,version_id=version,page=4,max_fields=1)['nextCursor']
for kwargs in [dict(version_id=version,page=5),dict(version_id='other',page=4),dict(version_id=version,page=4,kind='span')]:
 try:overview(n,cursor=c,**kwargs)
 except ValueError:pass
 else:raise AssertionError('cross scope accepted')
small={'lines':[{'line_id':'a','page_number':1,'text':'same','bbox':None},{'line_id':'b','page_number':1,'text':'same','bbox':None}]}
assert len(overview(small,version_id='v',page=1)['fields'])==2
big=copy.deepcopy(small);big['lines'][0]['text']='x'*40000
try:overview(big,version_id='v',page=1)
except ValueError:pass
else:raise AssertionError('oversized text silently truncated')
view=overview(small,version_id='v',page=1);view['fields'][0]['text']='mutated';assert small['lines'][0]['text']=='same'
assert overview(small,version_id='v',page=2)['coverage']['complete']
results['checks']='exact _rows IDs/text/bbox; bounded pagination complete; cross version/page/layer rejected; duplicates retained; oversized field rejected; detached response; empty page'
(root/'results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
