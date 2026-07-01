# Code S PPT Plan Test

You are acting as a delegated execution worker.

## Workspace

Repository root:

`/Users/xuhao/Documents/Other/context-infrastructure`

## Input

Read this PPTX:

`/Users/xuhao/Documents/Other/context-infrastructure/adhoc_jobs/code_s_plan_ppt_test/forgepane_mcp_plan_input.pptx`

If direct PPTX parsing is inconvenient, use this generated inspect fallback:

`/Users/xuhao/Documents/Other/context-infrastructure/adhoc_jobs/code_s_plan_ppt_test/forgepane_mcp_plan_input.pptx.inspect.ndjson`

## Output

Write exactly one output file:

`/Users/xuhao/Documents/Other/context-infrastructure/adhoc_jobs/code_s_plan_ppt_test/code_s_plan_result.md`

Do not edit any other repository file.

## Task

Convert the PPT into a plan-style execution brief.

The output must contain these sections:

- Summary
- Assumptions
- Phases
- Tasks
- Verification
- Risks
- Open Questions

Task requirements:

- Include at least 6 tasks.
- Every task must include owner, input, action, output, and verification.
- Clearly distinguish these three security boundaries:
  - public no-auth smoke endpoint
  - read-only adapter
  - shell-capable DevSpace
- Stay faithful to the PPT content. Do not invent unsupported facts.
- If you used the inspect fallback instead of parsing the PPT directly, say so in the output.

Final response should be brief and include:

- whether you completed the task
- which input you used
- which file you wrote
