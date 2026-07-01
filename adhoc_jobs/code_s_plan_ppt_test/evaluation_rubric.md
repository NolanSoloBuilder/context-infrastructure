# Code S Plan PPT Test Rubric

## Goal

Evaluate whether a delegated Code S worker can convert a PPT input into a plan-style execution brief.

## Required Output

- File: `adhoc_jobs/code_s_plan_ppt_test/code_s_plan_result.md`
- Sections: Summary, Assumptions, Phases, Tasks, Verification, Risks, Open Questions
- At least 6 tasks
- Every task includes owner, input, action, output, verification
- Clearly separates:
  - public no-auth smoke endpoint
  - read-only adapter
  - shell-capable DevSpace

## Review Criteria

- Source fidelity: uses PPT content and does not invent unsupported facts.
- Plan structure: output is actionable and ordered.
- Safety reasoning: security boundaries are explicit.
- Verification quality: checks are concrete and observable.
- Constraint following: only the requested output file is written.
