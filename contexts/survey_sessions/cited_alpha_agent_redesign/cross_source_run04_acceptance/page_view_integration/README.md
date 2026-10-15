# ML v3 page reading integration evidence

## Actual frozen version

`read_manifest.py` performed one explicitly authorized read-only GCS GET for the
Run04 checkpoint190 completed capture. It verifies expected user/workspace/
document/file and DocumentVersionId hash before using the receipt, then uses
production DocumentVersionStore.read to check configured bucket, path, size and
SHA. `actual-manifest.json` is mode600 in this private mode700 directory.
No parsing/provider/model submission or cloud write occurred.

`verify_actual.py` uses that exact manifest and version, retained official PDF,
and canonical retained provider JSON. All three bytes/SHAs match real receipts.
A local read-only map supplies these exact bytes to the real version verifier;
no repository/authorization bypass is added to the application. Production
load_verified replays normalization and checks the actual version scope. The
real authenticated attachment grant is copied from the known Run04 scope; this
is not a new HTTP authorization acceptance test.

p4/p5/p7/p8 all lines recover with exact original IDs/text/bbox, two calls each
under the tool's full JSON envelope 48KiB cap. Four selected citations compare
new v3 versus old v2 full entries, catalogs equal and restored catalog rebuilds.
No fake providerCallAttempted field or reconstructed manifest is used.
Results: `actual-results.json`.

## Byte boundaries and Pi

`toolEnvelopeBytes` measures JSON of content plus details, including escaping.
`modelTextBytes` is just the first text block UTF-8 size, not token count or full
provider request. Pi0.85.1 agent-loop.js createToolResultMessage retains details;
defaultConvertToLlm filters roles but does not remove details. The actual Python
vertex_messages.py then builds functionResponse from content/isError only, so
these duplicate details are not sent to Vertex. checkpoint_projection.py removes
details when proven equivalent; pendingEffects always stores full content.
The separate hostBudgetRemaining content block and runtime message framing are
outside the tool-local cap. Maximum measured tool envelope is48,718bytes.

## Application files

- mindspace/service/research_agent/document_read_view.py (new pure projection)
- mindspace/service/research_agent/immutable_document_tools.py (v3-only new tool)
- mindspace/service/research_agent/execution_service.py (new/default v3, explicit compatibility)
- mindspace/service/research_agent/report_tools.py (v3 retains v2 report contract)
- mindspace/service/research_agent/README.md
- tests/test_research_document_read_view.py (new portable tests)
- tests/test_research_execution_service.py (new/v1/v2/v3/missing checkpoint matrix)
- tests/test_research_report_content_compiler.py (unknown version now v999)
- tests/README.md
- runtime/research-tests/test-files.json
- runtime/research-tests/README.md

No Web/mobile direct endpoint contract changed: searched their service/api trees
for read_document/toolContractVersion, no direct consumers found. Backend must
support v3 checkpoint allowlist and new-capture default; Root owns those edits.
No commit/push performed. Existing unrelated dirty files preserved.
