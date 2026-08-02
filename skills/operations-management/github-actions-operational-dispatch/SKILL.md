---
name: github-actions-operational-dispatch
description: Dispatch and observe operational GitHub Actions workflows (infrastructure provisioning, deploys, snapshots, migrations, credential rotation) from a conversational agent. Use before calling workflow_dispatch on any operational pipeline, and whenever a chat-driven agent is asked to provision, deploy, snapshot, migrate, or rotate something through CI.
---

# GitHub Actions Operational Dispatch

Treat a conversational request to "run", "deploy", "tag", or "rotate" something as a request to operate a CI pipeline, not as a request the agent free-forms. `workflow_dispatch` inputs are load-bearing: wrong values silently take the wrong branch through the workflow's own routing logic, often exiting green while doing nothing or the wrong thing.

## 1. Build a per-repository catalog before dispatching anything

Do not infer a workflow's inputs, defaults, or hidden rules from its name or from memory. Before the first dispatch against a repository, read its actual `workflow_dispatch` block and any script it hands inputs to, and record: every input name, type, default, and required/optional; every input that is silently ignored by the scripts it's passed to (a dead input looks configurable but does nothing — flag it, don't expose it as if it works); every implicit rule the workflow enforces in code rather than in the YAML schema (input A requires input B; input C forces other inputs to fixed values; one action value bypasses normal switches). Store this catalog next to the target repository (its own docs, not a shared cross-repo skill) so it does not go stale the moment the workflow changes elsewhere.

## 2. Preflight before dispatch, not after

Run every rule from the catalog locally before calling `workflow_dispatch`. A rule violation must block the dispatch with a clear explanation, not be discovered ten or twenty minutes later inside a failed run. If a downstream system enforces an immutability or pin contract (e.g. a GitOps repo that only deploys an already-pinned image tag), check that contract before dispatch — requesting a value the downstream system will reject is not a workflow bug, it's a preventable preflight failure.

## 3. Confirm before dispatching, especially the dangerous fields

State every resolved input back to the user in plain language before dispatching — not "shall I proceed?" but the literal values that will be sent. Any input that is destructive, irreversible, or crosses an environment boundary (destroy, restore, a production/prod target, a traffic cutover, a credential rotation) requires the user to confirm that specific field, not a general "yes, go ahead". Never default a dangerous field to the enabled/destructive state; leave it off unless the user explicitly asked for it.

## 4. A completed run is not evidence that the operation happened

Actions provides `status` and `conclusion` on the run; use them to know when a dispatch has finished, never as the sole evidence that it worked. Independently verify the outcome the run claims to have produced — query the actual resource state, hit a health endpoint expecting the specific response the target's own operational runbook defines, or read the specific error a downstream rate limit / lock / quota system returns. A run that exits successfully while its own script silently matched zero targets is a known failure mode of this class of pipeline, not a hypothetical.

## 5. Stay inside the dispatch boundary

Only call `workflow_dispatch` (or equivalent) against workflows the operator has explicitly authorized for this target. Do not create branches, tags, or PRs to route around a workflow's trigger rules; do not modify the workflow, its scripts, or the repositories it deploys as a side effect of getting a dispatch to succeed. If a legitimate request cannot be satisfied within the existing trigger/authorization rules, say so and stop — that is a routing problem for the operator to fix, not something to bypass from a chat session.
