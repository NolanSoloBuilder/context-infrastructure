# Next local Run composition: read-only review

No process launch, cloud/model/DocAI call, database mutation, repository or harness edit was performed by this review.

## Shared transport and shutdown

`backend_app.py:21` constructs AuditedCheckpointStore with bucket only. `performance_audit.py` overrides only load/save and calls super; inherited `_run_http` therefore uses the process default checkpoint pool. The adapter, executor and callback factories all use this same store factory. No injected session bypass is present. Multiple store instances share transport; scope/hash checks remain each operation.

Blocking harness gap: `backend_app.py:31` uses bare FastAPI(), so production `launch.lifespan` cleanup is NOT installed. `paid_run.py:64-69` terminates then kills after ten seconds. This does not establish worker drain and may cut off an actual socket operation even after adding a lifespan.

Smallest temporary wiring correction (Root to apply): add a local asynccontextmanager lifespan with `try: yield; finally: await close_checkpoint_http_pool()` and instantiate FastAPI(lifespan=...). No production bootstrap import needed. Change launcher cleanup to retain worker PIDs/lock and report cleanup unknown when graceful termination has not completed; do not force-kill or unlink the active lock after ten seconds. On successful process exit close logs/unlink lock. This preserves the actual-thread drain guarantee; no finite graceful-exit promise is possible from 15/30s HTTP timeouts alone. Do not start a replacement while old processes still drain.

## Version and budgets

Current Backend checkpoint_service accepts v1/v2/v3 and seeds document placeholder v3 (line179). Current ML execution_service lines54-55 defaults fresh runs to v3, preserves a supplied checkpoint version and accepts all three. immutable_document_tools/report_tools implement v3. Existing Run04 checkpoint190 remains v2; do not mutate or reuse its checkpoint as a new v3 Run.

backend_app adapter limits and paid_run recorded contract/environment preserve 64 model /128 tool /1800seconds; reviewer2, SDK66 with one attempt/request, 16384 writer output,20second spacing,gemini3.8/global remain. Launcher records caller-provided full question unchanged; Root should read question from Run04 contract and compare exact equality before future launch, not shorten it to accelerate acceptance. `--reuse-recovered-provider` must remain explicit to avoid new paid parse.

## Zero-paid preflight (commands for Root, not run here)

First verify bound branches, isolated DB configs, no listeners18883/18884, no active lock requiring investigation. Do not print local-token/config contents.

    /Users/xuhao/Documents/Other/mindspace_backend/.venv/bin/python -m py_compile /tmp/cited-alpha-cross-run-7YGKhq/backend_app.py /tmp/cited-alpha-cross-run-7YGKhq/paid_run.py
    /Users/xuhao/Documents/Other/mindspace_backend/.venv/bin/python -m pytest -q /tmp/cited-alpha-cross-run-7YGKhq/test_observer_offline.py

For each repo launch its own uvicorn with PYTHONPATH pointing at harness and repo, ENV_MODE=local, MINDSPACE_SECRETS_YAML_FILE=<harness>/<backend|ml>-local.json, MONGODB_CONNECT_DISABLED=1, WORKSPACE_CLOUD_TASKS_ENABLED=false, MODEL_CALLS_DISABLED=true, BUSINESS_CANARY_ENABLE_PAID=no, GOOGLE_CLOUD_QUOTA_PROJECT=cited-alpha-20260701; bind127.0.0.1:18883/18884. Do not use paid_run.py for preflight. Keep credentials only in-process. A Python urllib client can read local-token into Authorization and request both /local-health, POST ML /local-preflight/callback with {}, and GET Backend /local-business/capabilities. Assert paidEnabled=false, wrong token rejection and nonexistent Run rejection; never POST /local-business/start, conversation, freeze, execute or review. Optional cross-source-preflight performs real owner reads but is not needed to prove pool closure. After local lifespan wiring, terminate owned Backend gracefully and wait for exit; separately offline test pool lifecycle (no GCS required).

## final191: established facts and limits

Timing-only performance spans show seq190 save succeeded starting06:10:44.936047 for7.6427seconds, and callback189 succeeded. Seq190 load started06:10:53.034007 and took3.7812seconds. Seq191 GCS save started06:10:56.933784 and succeeded in4.7431seconds (4,031,105bytes). Outer callback expectedSequence190 ended with ValueError, not success. Run deadline was06:10:55. Independently validated SQL pointer remained190 (4,029,869bytes), no checkedCandidate/report; terminal is failed/research_failed with “research execution did not acknowledge completion”.

`checkpoint_service._persist` awaits store.save before DAO.save_research_checkpoint. DAO rechecks live uncanceled Run/Step lease, deadline, execution scope and sequence transactionally before assigning pointer. Therefore GCS191 upload success is NOT a committed checkpoint. With recorded wall times, final DAO check occurred after recorded deadline; the explicit deadline predicate is sufficient to reject if evaluated then. However span only records ValueError type, not message or failed predicate; concurrent status/cancel/lease changes could also violate the same guard. Do not claim deadline was the unique observed cause or overwrite terminalReason as deadline_exceeded.

Backend ML transport raises the recorded acknowledgment error when the HTTP response status is not 200; that is the observed outer failure, not precise proof of the originating DAO predicate. To disambiguate next time add sanitized callback error classification/timestamp/lease-state evidence (no messages/thoughts), rather than infer from GCS object existence. No checkpoint191 promotion or old Run state mutation is justified.
