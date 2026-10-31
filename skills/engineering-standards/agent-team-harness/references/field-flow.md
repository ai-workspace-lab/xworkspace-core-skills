# Agent Team Harness field flow

This portable run card is subordinate to [Agent Team Harness](../SKILL.md), the selected TaskSource workflow, and linked engineering/operations standards.

## Intake

```text
[ ] Read repository instructions and confirm authorized scope.
[ ] Find the authoritative task and check for an existing duplicate.
[ ] Confirm goal, owner, business status, priority, and acceptance criteria in the TaskSource.
[ ] Record human-readable TASK_ID and immutable source ID (or explicit draft mapping).
[ ] Check active runs/ownership. If atomic claim/fencing is unavailable, serialize manually.
[ ] Bind run ID, executor/session, environment, isolated workspace/branch, and base revision.
[ ] Load harness-workflow and only the engineering/operations standards that apply.
```

## Source task comment

```text
Run: <run-id>
task_id: <stable-task-key>
Source Project node ID / item ID / issue node ID: <IDs-or-NOT_AVAILABLE>
Executor/environment: <non-sensitive labels>
Session binding: <approved reference; no token>
Workspace/branch/base revision: <workspace> / <branch> / <revision>
Evidence: <PR/artifact/check links and exact revision>
Next action or blocker: <bounded action or required decision>
```

## Handoff template

```markdown
# Handoff: <TASK_ID>
- Immutable source ID / relationships:
- Run ID / date:
- Prior run IDs (for recovery/takeover; preserve old records):
- Scope and explicit exclusions:
- Previous owner: stopped | active | unknown; evidence:
- Lease/fencing state and receiver confirmation:
- Executor/environment/session reference (non-sensitive):
- Workspace/branch/base revision/head revision/PR:
- Changed files and completed work:
- Checks: PASS | FAIL | BLOCKED | NOT_RUN (command, result, revision):
- Risks, unknown outcomes, and decisions needed:
- Next bounded action:
- Selected artifact IDs; archive: pending | file ID/URL/version/hash/idempotency key:
- Knowledge index: pending | task ID/source revision or archive ID/version/date/index reference:
```

## Closeout

```text
Engineering: PASS/FAIL/BLOCKED/NOT_RUN + exact revision/artifact
CI: PASS/FAIL/BLOCKED/NOT_RUN + run reference
Merge: PASS/FAIL/BLOCKED/NOT_RUN + PR/merge revision
Runtime: PASS/FAIL/BLOCKED/NOT_RUN + environment and boundary evidence
Business acceptance: authorized TaskSource owner decision
Archive: artifact ID + Drive/file ID + URL + version + integrity hash + source revision
Knowledge index: task ID + issue node ID + run ID + artifact ID + archive ref + QMD/index ref
Source task archive reference written: yes/no
Business completion authorized and applied: yes/no
```

Never mark missing evidence as passed. Resolve an uncertain write or dispatch by reading the target system before retrying.
