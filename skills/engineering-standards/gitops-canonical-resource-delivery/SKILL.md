---
name: gitops-canonical-resource-delivery
description: Use when designing or changing multi-cloud infrastructure and deployment orchestration where GitOps declarations must be the single source of truth for providers, accounts, regions, resource modes, state namespaces, and topology consumed by Terraform, selfhost, or serverless workflows.
---

# GitOps Canonical Resource Delivery

Use GitOps as the only runtime fact source for resource topology. Workflow repositories
may contain reusable adapters, renderers, validators, and orchestration code, but must not
keep a second authoritative environment matrix.

## Required flow

```text
GitOps environment resource matrix
        ↓
top-level orchestrator
        ├── selfhost orchestrator
        └── serverless orchestrator
```

The top-level orchestrator reads the selected GitOps commit and passes the resolved
namespace declaration to child workflows. Child workflows consume the same declaration;
they must not infer a provider from a global default or silently rebuild a second matrix.

## Declaration contract

Each resource row must make these decisions explicit:

- `namespace` and execution `order`;
- `management_mode`: `terraform`, `existing`, `existing-selfhost`, or a declared hybrid mode;
- provider and concrete account, or an explicit account reference resolved from the workflow profile;
- region, abstract profile, resource identity, lifecycle, and Terraform state namespace;
- application/topology references and whether XConnect, observability, or serverless is required.

Sensitive values never belong in GitOps. Store tokens, passwords, private keys, and connection
strings in the environment-scoped Vault contract.

## Routing and state rules

1. Checkout GitOps before validating or dispatching the matrix; pin the ref/SHA in the run summary.
2. Fail closed if the matrix is missing, malformed, unordered, or references an unknown provider.
3. Resolve provider and account per row. A workflow-level provider/account is only a fallback for
   rows that explicitly declare that reference; it must never overwrite a row's concrete account.
4. Terraform rows receive an isolated state key derived from environment, project, provider,
   concrete account, and namespace. Existing rows produce inventory/CMDB facts and never run
   Terraform create, import, apply, or destroy.
5. `plan`, `apply`, `deploy`, and `destroy` must preserve the same row identity. Do not use a
   changed provider, region, hostname, or profile with an existing state without an explicit
   migration/import plan and approval.
6. If a child workflow needs a resource detail, it reads the checked-out GitOps declaration or a
   validated output from the parent; it must not fall back to a hard-coded provider directory.

## Orchestrator boundaries

- The top-level orchestrator validates ordering, account/provider compatibility, dependency gates,
  approvals, and result aggregation.
- The selfhost orchestrator handles Terraform adapters, existing-host playbooks, host bootstrap,
  monitoring, and inventory output.
- The serverless orchestrator handles Cloud Run, Pages/Workers, Supabase, and edge routing.
- Neither child may mutate another namespace's state or reinterpret `all` as a private matrix.

## Verification checklist

Before a real mutation, verify:

- the GitOps matrix is the exact commit intended for the run;
- every namespace appears once and execution order is contiguous;
- provider, account, region, profile, management mode, and state key match the declaration;
- Terraform rows produce an isolated plan and existing rows produce no Terraform action;
- serverless and selfhost consumers read the same environment topology;
- no workflow, script, or test points to a repository-local runtime matrix;
- `destroy` scope excludes permanent/shared services and external resources unless separately approved.

When a legacy matrix exists, remove it from runtime paths after the GitOps source is available.
Keep only a non-authoritative test fixture if a schema test needs one, and label it clearly as a
fixture. Never let a fixture be used by a deployment workflow.
