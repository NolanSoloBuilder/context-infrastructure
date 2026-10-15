import sys,json,hashlib,asyncio
from pathlib import Path
sys.path.insert(0,'/Users/xuhao/Documents/Other/mindspace_ml_backend')
from mindspace.service.research_agent.document_version_service import DocumentVersionService,_json
from mindspace.service.research_agent.immutable_document_tools import ImmutableDocumentResearchTools
from mindspace.service.research_agent.document_read_view import MAX_BYTES
root=Path(__file__).parent
async def main():
 v=json.loads((root/'actual-version.json').read_text());m=(root/'actual-manifest.json').read_bytes()
 raw=Path('/Users/xuhao/Documents/Other/context-infrastructure/contexts/source_materials/cited_alpha_cross_source_tesla_2024/05dfde334f800ec5f0ee140c0dd78409f24ad775e11a0c68f8a6b534b04cafdc.pdf').read_bytes()
 provider=_json(json.loads(Path('/tmp/cited-alpha-cross-source-business-02/recovered-provider-readonly/providerDocuments.json').read_text()))
 objects={}
 for key,data in [('rawReceipt',raw),('manifestReceipt',m),('providerReceipt',provider)]:
  r=v[key];assert len(data)==r['byteSize'] and hashlib.sha256(data).hexdigest()==r['sha256'],key;objects[r['objectUri']]=data
 class Store:
  async def read(self,r):
   data=objects[r['objectUri']];assert hashlib.sha256(data).hexdigest()==r['sha256'];return data
 service=DocumentVersionService(store=Store())
 doc=v['documentId'];grant={'documentId':doc,'fileItemId':'uf_78b818ac18f04d789728734ad9ed41e1','fileId':v['fileId'],'version':v}
 opts=dict(user_id=v['userId'],workspace_id=v['workspaceId'],authorized_documents={doc:grant},version_service=service)
 subject=ImmutableDocumentResearchTools(**opts,tool_contract_version='research-tools/v3')
 legacy=ImmutableDocumentResearchTools(**opts,tool_contract_version='research-tools/v2')
 original=await subject._load(doc) # Actual scope/hash/raw/provider/normalizer full verifier.
 results={}
 for page in (4,5,7,8):
  fields=[];cursor=None; sizes=[]
  while True:
   args={'document_id':doc,'page_number':page}
   if cursor:args['cursor']=cursor
   response=await subject.execute({'name':'read_document_page','arguments':args})
   envelope=len(json.dumps(response,ensure_ascii=False).encode());assert envelope<=MAX_BYTES
   sizes.append({'toolEnvelopeBytes':envelope,'modelTextBytes':len(response['content'][0]['text'].encode())})
   value=response['details'];fields.extend(value['fields']);cursor=value['nextCursor']
   if cursor is None:break
  expected=[r for r in original['lines'] if r['page_number']==page and r['text'].strip()]
  assert len(fields)==len(expected)
  for f,r in zip(fields,expected):assert f['id']==r['line_id'] and f['text']==r['text'] and f['bbox']==r['bbox']
  # Citation representative preserves original full entry exactly; all field lookups above verified.
  f=fields[len(fields)//2];frame={'name':'cite_document_field','arguments':{'document_id':doc,'kind':f['kind'],'id':f['id']}}
  assert await subject.execute(frame)==await legacy.execute(frame)
  results[page]={'fields':len(fields),'calls':len(sizes),'sizes':sizes}
 assert subject.catalog==legacy.catalog
 restored=ImmutableDocumentResearchTools(**opts,tool_contract_version='research-tools/v3',catalog=subject.catalog)
 await restored.initialize();assert restored.catalog==subject.catalog
 (root/'actual-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
asyncio.run(main())
