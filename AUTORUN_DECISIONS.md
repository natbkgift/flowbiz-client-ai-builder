# AUTORUN_DECISIONS

No overrides active for this PR. Standing authorizations are logged below.

## AUTO_RUN Standing Defaults

1) Merge Strategy Default
- Default merge method: REBASE (fast-forward). This is the standing default for automated merges and takes precedence over the general preference for `SQUASH` in `PR_POLICY.md`.
- If a branch ruleset strictly requires a different method (e.g., squash), that requirement will be honored.

2) Unknown Commit Handling
- If a commit appears “not created by agent”: STOP and CONTROLLED_HALT unless an explicit authorization exists in Authorization Log.

3) CI/Checks Handling
- Never merge unless all required checks are present and green.
- If checks are pending/queued: wait for a short interval (e.g., 60s) before re-checking. If polling is unavailable or checks remain pending → CONTROLLED_HALT (“CI pending — awaiting next execution cycle”).
- CI fix loop maximum: 3 attempts; then CONTROLLED_HALT.

4) Fail-Safe / main Not Green
- If main is red after merge or a critical workflow fails: open HOTFIX PR immediately to restore green before continuing milestones.

5) Human Approval Declaration
- PR Final Declaration: always include "Approved by: <human> / Date: <YYYY-MM-DD>" when AUTO_RUN_MODE is STRICT and repo policy requires it.
- If approver/date is missing and required: CONTROLLED_HALT.

6) Evidence Discipline
- If guardrails require evidence index updates: always append a new entry in docs/audit/EVIDENCE_INDEX.md for every PR.
- Evidence must include CI run link(s) when available.

## Authorization Log
| Date | Authorized By | Mode | Scope | Reason | Status |
| --- | --- | --- | --- | --- | --- |
| 2025-12-29 | natbkgift | GUIDED | PR-016 deferral | Architectural review required before re-implementation | ACTIVE |
| 2025-12-30 | natbkgift | STRICT | AUTO_RUN Standing Defaults | Reduce routine confirmations; keep automation audit-safe | ACTIVE |
