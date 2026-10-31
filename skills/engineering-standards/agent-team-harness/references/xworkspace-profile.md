# XWorkspace profile: GitHub Projects + Bridge + QMD + Drive

This is one concrete profile for [Agent Team Harness](../SKILL.md), not a core dependency contract. It captures the user's preferred operating model. The profile is a design reference; current runtime integration and permissions have **not** been verified.

## Capability mapping

| Harness capability | XWorkspace candidate | Boundary |
| --- | --- | --- |
| TaskSource | GitHub Projects and Issues across `ai-desktop-lab`, `ai-workspace-infra`, `ai-workspace-lab`, `ai-workspace-services`, `ai-workspace-xstream` | The Project/Issue owns goal, assignee, priority, business status, and acceptance criteria. Search before creating; ask before creating a missing Issue. |
| Executor | Local/remote Codex, Claude Code, or another authorized agent runtime | Records host, environment, agent/session binding, isolated worktree/branch, base/head SHA, PR, and evidence. Runtime availability is checked per host; do not assume. |
| CoordinationStore | XWorkmate Bridge with PostgreSQL as a candidate transactional store | Run/session bindings, attempts, atomic lease, heartbeat, fencing, event/outbox and archive-job facts only. Does not own Project business state. Do not claim atomicity until verified. |
| KnowledgeIndex | QMD | Rebuildable handoff/knowledge pointers only; never task status, lease, or lock. Persist an index reference, not an authoritative result. |
| ArchiveStore | An explicitly approved Google Drive destination | Only selected sanitized summaries/results/artifacts; stable Drive file ID+URL/version/hash; task/tenant ACL. No raw chats, secrets, or production data. |
| Transport | XConnect | Private connectivity only; it does not grant identity or authorize an operation. |

Persist stable `task_id`, source Project node ID, Project item ID, linked `source_issue_node_id` when present, and Project memberships. If a GitHub Issue appears in multiple Projects, keep one Issue node ID as canonical task identity and store each Project item as a membership. Preserve draft-item-to-Issue mapping when converting a draft. Human-readable key convention:

```text
<org>/<repo>#<issue-number>
<org>/<repo>#draft-<opaque-local-id>
```

The GitHub node ID is the immutable identity when available. Drafts without a stable global key get a generated opaque ID linked to the actual Project item ID; never invent an Issue number. Use a path-safe slug in filenames, not raw `/` or `#`, and put the exact `TASK_ID` in the file header.

## Operational flow

1. Use `gh project list` and `gh project item-list` (or the authorized equivalent) to inspect the five organizations' Projects. Check pages, fields, draft items, linked Issues, and memberships; do not assume a single project or repository is complete.
2. Find the existing canonical task and check its current business owner/status/acceptance criteria. If no Issue exists, propose the Issue content and obtain user approval before creation. Business fields are changed only in Project/Issue.
3. Register a technical run in the coordination layer. Add an authorized Issue comment with host/environment/agent/session reference/worktree/branch/base SHA. Keep runtime/session details out of business status fields; do not post tokens or secret host configuration.
4. Execute under `harness-workflow` and the applicable engineering standards. Use `TASK_ID` in PR/commit references per repository convention. Report exact SHA and checks; `Done` in the Project is a business acceptance decision, not a synonym for agent completion.
5. For machine handoff, write `handoffs/<safe-task-id>-<date-or-run>.md` with the complete boundary, authority, current SHA, evidence, unknowns, and next step. Link it from the source task. A recovery/manual takeover creates a new `run_id` linked to the original task and previous run; never overwrite old run records. Receiver confirms ownership; absent effective atomic claim/fencing, serialize manually.
6. After authorized acceptance, select only the approved summary/results/artifacts; redact sensitive data. Compute SHA-256 and use a stable idempotency key scoped by task/access domain, `artifact_id`, and version. Verify Drive ACL is inherited and no broader than task/tenant access. Record Drive `file_id`, URL, version, hash, date, and source SHA. Create `-vN`/new version; never overwrite or delete old evidence. On uncertain upload, read Drive first before retry.
7. Backfill the Drive file ID and URL to the source task. Then apply the authorized `Done` transition. If archive fails, do not redo engineering; retry only archive using the same idempotency key after outcome reconciliation. Retry QMD indexing separately.
8. QMD metadata contains `task_id`, `source_issue_node_id`, `run_id`, `artifact_id`, source SHA or Drive `file_id`/URL, archive version/hash/date, and QMD index reference. It is rebuildable and never a fact source. Never index raw chat, secrets, private environment values, or unauthorized production data. On access revocation, mark archive/index references and support authorized clear; actual permission changes or deletion still require explicit authorization.

## Profile-specific scheduled audit

When an authorized operator requests a hygiene report, identify completed Project items without archive links and PRs without task references. Report candidates with evidence; do not silently modify Project items, close another person's task, create automation, bulk-upload, alter Drive sharing, or delete Drive files. Any recurring report requires separate authorization.

## Profile-specific proof stages

1. G0: inspect real Projects, permissions, identity mappings, Bridge/PG/QMD/Drive contracts, retention and ACL behavior.
2. One organization: read-only sync/identity/deduplication check.
3. One host and one non-production task: manually bind one agent session and prove the full task-to-evidence-to-archive loop.
4. Same agent across two hosts: prove atomic lease, heartbeat, fencing at side-effect boundaries, interruption recovery, and uncertain outcome handling; otherwise remain serialized.
5. Add heterogeneous agents and the other organizations only after earlier stages pass.

Mark every unrun stage `NOT_RUN`. A design note, local configuration, or passing documentation linter is not runtime evidence.
