import sys,json,hashlib,asyncio,os
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,'/Users/xuhao/Documents/Other/mindspace_ml_backend')
import google.auth
from google.auth.transport.requests import AuthorizedSession
from mindspace.service.research_agent.document_version_store import DocumentVersionStore
from mindspace.service.research_agent.document_version_service import _json
async def main():
 state=json.load(open('/tmp/cited-alpha-cross-source-business-04/independent-checkpoints/190.json'))
 capture=state['documentCaptures']['doc_file_e9aca68920734fabbc3a27b72d27cfa3'];v=capture['version']
 assert v['userId']=='pdf-b7239c049f014f' and v['workspaceId']=='workspace-67c131c6-2579-4b48-aa05-d85cdbb94637'
 assert v['documentId']=='doc_file_e9aca68920734fabbc3a27b72d27cfa3' and v['fileId']==capture['fileId']
 unsigned=dict(v);identity=unsigned.pop('documentVersionId');assert identity=='dv-'+hashlib.sha256(_json(unsigned)).hexdigest()
 credentials,_=google.auth.default(scopes=['https://www.googleapis.com/auth/devstorage.read_only'])
 session=AuthorizedSession(credentials)
 try:
  store=DocumentVersionStore(writer=SimpleNamespace(bucket='cited-alpha-workspace-source-snapshots',session=session))
  raw=await store.read(v['manifestReceipt'])
 finally:session.close()
 root=Path('/tmp/cited-alpha-page-view-integration');(root/'actual-manifest.json').write_bytes(raw);(root/'actual-version.json').write_text(json.dumps(v));os.chmod(root/'actual-manifest.json',0o600)
 print('manifest SHA and byteSize validated; read-only GET complete')
asyncio.run(main())
