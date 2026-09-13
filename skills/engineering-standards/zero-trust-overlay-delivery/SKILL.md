---
name: zero-trust-overlay-delivery
description: Design, implement, or review a Zero-driven XConnect overlay network spanning XConnect Zero/Accounts, Gateway, One clients, GitOps, Playbooks, Vault, IaC, and deployment workflows. Use for WireGuard-over-VLESS, signed enrollment/configuration, Gateway/One runtime roles, or UAT-to-PROD overlay delivery. Do not use for a static WireGuard-only network with no controller.
---

# Zero-Trust Overlay Delivery Standard

Use this standard when a task changes an XConnect/Zero overlay control plane, a
Gateway, a controlled One client, its WireGuard-over-VLESS transport, or the
automation that deploys and validates those parts. Read the repository map and
the target repository's existing contract before changing any layer. This
standard complements, rather than replaces, `config-as-code-spec`,
`infrastructure-as-code-spec`, `ci-cd-workflow-spec`, and
`multi-environment-delivery-and-release`.

The objective is a repeatable, controller-driven data plane:

```text
XConnect Zero / Accounts
  -> signed enrollment, configuration, and policy
XConnect Gateway
  -> Xray transport and WireGuard hub
XConnect One
  -> Xray transport and WireGuard client
```

The control plane never carries VPN packets. Gateway and One never invent
policy, sign their own configuration, or upload device private keys.

## 1. Ownership is a hard boundary

| Layer | Owns | Must not own |
| --- | --- | --- |
| `accounts` / Zero | tenant, network, device, enrollment, policy, signed configuration, ACK/session metadata | WireGuard or transport runtime processes; device private keys |
| `portal` | user-scoped management UI and BFF calls to Accounts | Vault secrets, device credentials, peer private keys |
| `gitops/vpn-overlay` | non-sensitive desired topology, role/lifecycle, transport policy, release pins, address allocation intent | keys, invitations, VLESS credentials, controller tokens, SSH credentials, rendered peer files |
| `iac_modules/vpn-overlay` | reusable cloud resources, security groups, instance/lease shape, CMDB outputs | OS packages, systemd units, device enrollment, WireGuard/Xray configuration |
| `playbooks/roles/vhosts/vpn-overlay` | idempotent OS runtime roles, package install, directories, service units, health probes | cloud resources, static private keys, controller policy decisions |
| `platform-ops-toolkit` | OIDC/Vault injection, ref validation, orchestration, enrollment execution, evidence collection and cleanup | unpinned builds, long-lived secrets, a second desired-state store |
| Vault | TLS/VLESS/signing/host-login materials and secret references | public topology and non-sensitive release declarations |

When ownership is unclear, stop and make it explicit before adding a field or
script. Do not copy state across two layers merely to make a workflow easier.

## 2. No target-selection hardcoding

An IP address, hostname, CIDR, release tag, Vault environment path, instance
shape, security-group rule, interface name, port, or target node list is a
parameter whenever it can vary by environment, run, or node. It MUST come from one authoritative
declaration or a validated runtime input; it MUST NOT be duplicated as a
literal in a shell script, test probe, playbook default, or workflow fallback.

Apply these rules:

1. Put non-sensitive, durable defaults in the environment GitOps declaration.
   A Workflow may provide an ephemeral override only for that run (for example,
   a temporary operator SSH `/32` allowlist); it must not write the override
   back into GitOps.
2. Parse declarations structurally with a YAML/JSON parser. Do not recover
   nested topology values with indentation-sensitive `grep`, `awk`, or `sed`.
3. Validate every address at the boundary: canonical IPv4/IPv6 form as
   applicable, permitted prefix length, membership in the declared overlay
   CIDR, uniqueness, and difference between Gateway and device addresses.
4. Derive every consumer value from the same normalized topology object. A
   Gateway bootstrap, One handoff, route probe, and test assertion must use the
   resolved address, not four independent literals.
5. Missing target values fail closed. A production address, domain, controller,
   or Vault path is never a fallback for UAT or a manual invocation.

Loopback listener addresses and protocol constants are allowed only when they
are part of a documented runtime contract and do not identify a deployment
target.

## 3. Keep Zero as the source of truth

The operational path is:

1. Zero authorizes a network, Gateway, One device, and policy.
2. Gateway and One authenticate, obtain a signed configuration, verify it,
   render their private local runtime state, apply it, and ACK the applied
   revision.
3. The Gateway accepts only peers present in its signed configuration; One
   installs only the CIDRs and Gateway key it is authorized to use.

`GitOps` may declare the network intent but cannot contain generated peer
configuration, a device private key, an invitation, a VLESS UUID, or a signed
configuration. Legacy roles that consume static `overlay_config_path` or
`overlay_keys_path` are not a substitute for this flow. Add a Zero-driven
Gateway or One role/entry point rather than modifying a static role until it
silently becomes a second controller.

## 4. Data-plane contract and exposure

The packet path is declared by the selected transport profile. For the current
XConnect baseline, the path is:

```text
One WireGuard -> local Xray transport -> VLESS/TLS/XUDP
  -> Gateway Xray -> Gateway WireGuard -> overlay resource
```

- Gateway and One each manage their own external Xray and WireGuard runtime.
  The One CLI coordinates runtime bootstrap, signed-config verification,
  rendering, start/stop, status, and ACK; it does not require XConnect App.
- Public ingress is an explicit transport policy. The current stable profile
  uses restricted TCP 443; this is a profile value, not a universal default.
  WireGuard UDP is transported inside the selected transport and is not a
  public security-group rule unless a separately reviewed profile requires it.
  Additional transport ports remain disabled until their signed-config and
  runtime contract exist.
- TLS keys, VLESS credentials, Reality material, enrollment credentials, and
  private keys are injected from Vault into protected local state. Logs,
  GitOps, workflow summaries, handoff artifacts, and documentation contain
  references and redacted identifiers only.

## 5. Runtime roles and lifecycle

Runtime roles MUST be idempotent and narrowly scoped:

- **Gateway role:** install checksummed/pinned Gateway, Xray, and WireGuard
  artifacts; prepare protected state and TLS directories; configure required
  forwarding; run `init`/`join`/`sync`/`up`; expose safe status probes.
- **One role:** install checksummed/pinned One, Xray, and WireGuard artifacts;
  prepare protected state; run `join`/`sync`; let the One CLI render and own
  its Xray/WireGuard runtime; expose `status`, `diagnose`, and `down`.
- Configuration changes must verify syntax and readiness before service reload.
  A role must not generate peer keys or overwrite a signed configuration.
- Dynamic/Spot nodes carry a lease and lifecycle label. At expiry, revoke or
  deactivate them in Zero/Gateway using an idempotent action; never infer that
  an instance disappearance has already revoked its network access.

## 6. Workflow design and evidence

Keep build, infrastructure provisioning, runtime deployment, and formal Zero
enrollment as separate named stages. Resolve immutable artifact refs before
mutating a host. Workflow dispatch should expose only the minimal useful
parameters; preserve stable GitOps defaults and derive reviewed immutable refs
when an input is omitted.

An overlay run is successful only when it records all applicable evidence:

- the resolved GitOps/IaC/artifact refs and topology identifiers;
- Gateway and One service status after signed `sync`;
- applied configuration revision and ACK, treated separately from transport;
- an exact expected WireGuard peer handshake, not merely an observed peer;
- private-network ping and a bounded HTTP marker check;
- redacted failure diagnostics and a recoverable cleanup/lease outcome.

Cloud-only transport checks and optional macOS/Windows handoffs are separate
stages. A manual desktop check must never block or falsely pass the
Gateway/Linux acceptance result.

## 7. Environment and data safety

- UAT may reset **overlay-only** test data when the runbook names the exact
  tables/resources, validates the environment, and is retry-safe when an
  object is already absent. It must never touch users, subscriptions, billing,
  invoices, or historical usage.
- Production schema evolution is additive and rollback-aware: take and verify a
  backup, add compatible structures, backfill in bounded steps, release a
  compatible consumer, validate zero remaining references, and only later
  retire legacy columns/tables. Maintenance downtime may be explicit; data loss
  is never an acceptable shortcut.
- Never use broad deletes, `CASCADE`, reset-by-prefix, or a blanket public
  ingress rule to repair an enrollment or handshake failure. Inspect the
  controller exchange, signed revision, runtime status, and peer state first.

## 8. Learning loop: turn incidents into durable guards

After each failed or ambiguous overlay run, record a short, redacted outcome in
the PR or issue: triggering inputs, violated invariant, owning layer, evidence,
and the preventive guard selected. Then add the smallest durable guard in the
layer that owns the invariant:

Use this compact feedback record so the lesson can be reused across providers,
environments, and transports:

```text
Observed: <redacted symptom and exact failing checkpoint>
Invariant: <what must be true, independent of host/name/provider>
Owner: <Zero | GitOps | IaC | Playbooks | runtime | workflow | test>
Guard: <assertion, schema rule, fixture, probe, or review check>
Evidence: <test/command/run reference, with secrets and target details redacted>
```

Generalize the invariant, not the incident's literal value. For example, turn
“this address was wrong” into “all consumers use one validated address from the
normalized topology”; do not add that address as a new default. A lesson is
ready to become a reusable rule only when the guard can fail on a future change
and can be rerun without access to the original host or secret.

| Failure class | Durable guard |
| --- | --- |
| address/role drift | normalized topology validation plus a fixture proving consumers receive the same resolved value |
| stale or missing release asset | immutable-ref preflight and checksum/artifact existence test |
| Vault JWT mismatch | exact workflow-ref/role contract test; do not widen claims |
| ACK without a usable tunnel | exact peer-handshake plus private ping/HTTP acceptance test |
| non-idempotent reset or cleanup | rerun test for already-absent/previously-applied state |
| secret exposure in diagnostics | redaction test and secret rotation process, never a log allowlist |

Only promote a local workaround to this standard after it has an identified
invariant and a repeatable test or review check. Keep incident facts redacted;
the skill teaches the prevention mechanism, not the secret, host, or one-off
address involved.

## 9. Review checklist

Before merging an overlay change, confirm:

- [ ] Every mutable target resolves from GitOps or a validated run input, with no
      duplicated deployment literals.
- [ ] GitOps, IaC, workflow, runtime role, and Accounts have one clear owner
      for each field.
- [ ] Zero remains the sole issuer of enrollment, policy, signed config, and
      peer authorization.
- [ ] Vault injection uses narrow OIDC roles and no secret reaches Git,
      artifacts, logs, or workflow inputs.
- [ ] Gateway/One roles use immutable artifacts and are safe to rerun.
- [ ] UAT reset scope is overlay-only; production migration is additive and
      backup-verified.
- [ ] Acceptance proves the expected handshake and private traffic, not only
      provisioning, ACK, or a UI status.
- [ ] Any new failure mode adds a regression fixture, preflight, or review
      invariant in its owning layer.
