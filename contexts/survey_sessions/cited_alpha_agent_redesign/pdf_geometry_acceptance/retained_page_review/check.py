import sys,json,hashlib,base64,importlib.util
from pathlib import Path
from copy import deepcopy
sys.path.insert(0,'/Users/xuhao/Documents/Other/mindspace_ml_backend')
from mindspace.service.document_ai.layout_parse_adapter import DocumentAILayoutParseAdapter
from mindspace.service.research_agent.page_rendition import retained_page_rendition
from mindspace.service.research_agent.document_geometry import derive_field_geometry
spec=importlib.util.spec_from_file_location('backend_rendition','/Users/xuhao/Documents/Other/mindspace_backend/mindspace/service/ml_service/research_page_rendition.py');backend=importlib.util.module_from_spec(spec);spec.loader.exec_module(backend)
root=Path('/tmp/cited-alpha-page-rendition-cross-review')
provider_path=Path('/tmp/cited-alpha-cross-source-business-02/recovered-provider-readonly/providerDocuments.json')
provider_bytes=provider_path.read_bytes();docs=json.loads(provider_bytes)
raw=Path('/Users/xuhao/Documents/Other/context-infrastructure/contexts/source_materials/cited_alpha_cross_source_tesla_2024/05dfde334f800ec5f0ee140c0dd78409f24ad775e11a0c68f8a6b534b04cafdc.pdf').read_bytes()
rawsha=hashlib.sha256(raw).hexdigest()
# Explicit offline metadata context; not a claimed production sealed DocumentVersion.
version={'parserVersion':'research-document-layout-normalizer/v1','documentVersionId':'offline-cross-repo-context', 'rawReceipt':{'sha256':rawsha},'providerReceipt':{'sha256':hashlib.sha256(provider_bytes).hexdigest()}}
parsed=DocumentAILayoutParseAdapter().to_parse_result(document_ai_documents=docs,document_id='offline-original-provider',source='conversation_upload',parse_run_id='offline-review',sha256=rawsha,parser_version=version['parserVersion']).model_dump(mode='json')
selected=[r for r in parsed['lines'] if (r['page_number']==4 and r['text'].strip() in ['25,707','2,064']) or (r['page_number']==31 and r['text'].strip() in ['Net cash provided by operating activities','(37)']) or (r['page_number']==26 and r['text'].strip() in ['Operating Cash Flow ($B)','Free Cash Flow ($B)'])]
results=[]
for record in selected:
 locator={'kind':'line','id':record['line_id']}
 metadata,image=retained_page_rendition(version=version,provider_documents=docs,record=record,locator=locator)
 wire=json.loads(json.dumps(metadata))
 backend.validate_page_rendition(wire,version=version,locator=locator,page_number=record['page_number'])
 assert backend.decode_page_image(base64.b64encode(image).decode(),wire)==image
 expected=next(p for d in docs for p in d['pages'] if p['pageNumber']==record['page_number'])
 assert image==base64.b64decode(expected['image']['content'])
 assert wire['surface']=='retained_provider_page'
 geometry=derive_field_geometry(raw_pdf=raw,provider_documents=docs,record=record,parser_version=version['parserVersion'])
 assert geometry['locationPrecision']=='page' and geometry['bboxNormalized'] is None
 for field,value in [('fieldId','wrong'),('pageNumber',99),('rawSha256','0'*64),('providerSha256','0'*64),('documentVersionId','wrong'),('surface','pdf')]:
  bad=deepcopy(wire);bad[field]=value
  try:backend.validate_page_rendition(bad,version=version,locator=locator,page_number=record['page_number'])
  except ValueError:pass
  else:raise AssertionError(field+' mismatch accepted')
 try:backend.decode_page_image(base64.b64encode(image[:-1]+b'x').decode(),wire)
 except ValueError:pass
 else:raise AssertionError('corrupt image accepted')
 results.append({'page':record['page_number'],'fieldId':record['line_id'],'text':record['text'].strip(),'imageSha256':wire['sha256'],'width':wire['width'],'height':wire['height'],'bbox':wire['bboxNormalized'],'originalPdfPrecision':geometry['locationPrecision']})
for quote in ['2,064','(37)']:
 pair=[r for r in results if r['text']==quote];assert len(pair)==2 and pair[0]['fieldId']!=pair[1]['fieldId'] and pair[0]['bbox']!=pair[1]['bbox']
assert len(results)==8
(root/'result.json').write_text(json.dumps({'boundary':'Actual ML normalizer+rendition -> actual Backend metadata validator+Pillow decoder; offline context, not full authenticated HTTP/DAO or production sealed version.','cases':results},indent=2))
print(json.dumps({'cases':len(results),'crossRepoMetadataAndDecode':'passed','tamperedScopeAndBytes':'rejected','pdfFallback':'page','duplicateValues':'distinct field IDs and bboxes'}))
