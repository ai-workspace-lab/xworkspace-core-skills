# Target-side generation reconciliation

Use for an explicitly authorized one-way reconciliation from a serving generation
to a recovery generation. Parameterize environment, source/target generation,
database identity, host, release and schema version. Do not infer authorization
to touch another generation from a similar hostname or shared environment.

## Immutable source boundary

- Run backup, staging, preview, merge and validation on the target host only.
- Read source data through a least-privileged database connection in a consistent,
  read-only transaction. Do not install tools, create users, change configuration,
  pause writers, restart services or write temporary files on the source host.
- Do not switch public DNS, shared Vault or serving traffic during a rehearsal.
- A consistent snapshot is current at its snapshot boundary, not indefinitely
  real-time. Record the boundary; do not claim zero lag while source writes continue.

## Mandatory six gates

1. Back up the target and actually restore into an isolated database. Validate
   schema, migration version/dirty state, counts and stable data fingerprints.
   Backup existence or checksum alone is insufficient. Keep secrets out of logs.
2. Read a consistent source snapshot; validate unique identity mappings. Missing,
   ambiguous or incompatible user/proxy identities stop the merge. Never guess.
3. Produce a read-only preview for explicitly reviewed tables and columns. Bind
   source/target identities, source snapshot contents, target baseline, schema,
   migration receipts and executor SHA to review evidence. Reject stale plans.
4. Quiesce and verify target writers through the execution owner. Recheck the
   approved plan under bounded locks; apply in one transaction without DDL,
   table recreation, truncation or broad replacement.
5. Append absent immutable traffic/financial facts; identical replay is a no-op.
   A matching key with different content rolls back everything. Preserve target-only
   facts. Mutable quota snapshots must not overwrite independent target activity;
   require a proven reconciliation rule or stop. Never refill quota implicitly.
6. Verify unchanged schema and migration receipts, unchanged user identities and
   protected tables, plus expected quota/traffic/financial fingerprints. Record
   aggregate results without user-level identifiers. Resume target services only
   through the reviewed runbook and verify their runtime behavior separately.

## Ownership and failure handling

- Toolkit/Pipeline: selection, authorization, evidence validation and final gate.
- GitOps: desired state and configuration references only; not runtime CMDB.
- IaC Modules: cloud operations and authoritative resource/CMDB facts.
- Playbooks Roles: target backup, isolated restore, writer quiescence, reconciliation
  invocation and service verification. Domain merge semantics belong in the service
  migration tool, not duplicated in shell SQL.
- Authentication success does not prove SSH or database reachability. On timeout,
  report the exact failing gate; do not disable host-key checking, open firewalls
  elsewhere or mutate the source to work around target connectivity.
- Failure before commit leaves target data unchanged; stop and inspect. After
  commit, prefer forward correction. Restoring over the target can erase new
  transactions and requires a separate reviewed recovery decision.
- Tests use disposable isolated fixtures, never default live test users. Local
  tests, merged PRs, deployment and live acceptance are separate evidence gates.
