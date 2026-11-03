---
name: sentinel-xdr-solution-deployer
description: Deploy and verify Sentinel Analytic Rules and Defender XDR Custom Detections disabled in an approved non-production environment.
---

# Deploy Sentinel and XDR detections safely

Use this skill only after full validation and packaging have passed, or after
the canonical workflow has accepted a fresh, applied partial package meeting
the strict over-50% threshold. For a partial package, deploy only the exact
selected AR/CD content bound by its current package-selection plan; excluded
items remain visible but are not deployment failures for that selected scope.
Deployment is a write operation and always requires explicit user approval for
the exact subscription, resource group, workspace, solution, and deployment
mode.

## Modes

### One early scope-consent request

After the Qualification target is locked and before Discovery, review the
current local scope plan and ask once for consent to the bounded potential
action groups. Show the exact target, solution/version, inventory counts,
eligible IDs and caps, current package identity, resource types, and which
conditional prerequisites are proven, absent, or unknown. Include:

1. disabled Sentinel alert-rule and Graph Custom Detection creation or
   reviewed updates;
2. conditional fallback DCR/DCE creation;
3. conditional creation of a proven-absent custom-log table;
4. reviewed mock telemetry ingestion, including payload, records/batches,
   stream, estimated bytes/cost, and retention impact;
5. controlled alert parity, with exact pairs, proposed time window, bounded
   enable/restore operations, and abort restoration;
6. full-package installation and selected XDR Content Hub registration; and
7. explicitly owned cleanup/deletion, listing exact resources and ownership
   evidence while excluding pre-existing or unowned resources.

Show a structured consent form with **Approve the broadest currently bounded
and available scope** preselected as the suggested default, plus **Select
components**, **Revise the plan**, and **Decline advance consent**. This default
is only a proposal. Display each proposed component, cap, exact target,
resource family, and package flag/value before asking the user to submit.
Require affirmative submission/confirmation of the displayed scope before
recording consent; a preselected choice alone, cancellation/closure, decline,
or missing response records no approval. Permit narrowing, revision, or
decline.

The suggested broad scope includes only components supported by the current
consent CLI and fully bound to current evidence. If available, it can include
the disabled Sentinel-AR/Graph-CD pair and separate later
`fullPackageAcceptance`. For package acceptance, show every exact current
package-selection flag and its boolean value. If the plan exposes five valid
flags and the broad proposal selects all five, list each flag by name with
`true`; never hide selections behind an “all” label or invent flags. Do not
silently include unknown/provisional ingestion, DCR/DCE, custom-table,
parity, or cleanup scopes. If the broadest scope cannot be fully bound, suggest
only the largest valid bounded subset and explicitly list unavailable or
excluded groups with reasons.

Persist only the exact, affirmatively submitted component and flag selection
after verifying it against the current plan. Ask again only if the target,
plan identity, action/resource families, payload, caps, package flags, or
cleanup ownership changes. Missing or unknown scope is provisional, not
unlimited; denial does not block independent read-only validation.

The current CLI can persist consent for the direct disabled AR/CD pair,
`fullPackageAcceptance`, `mockTelemetryIngestion`, `fallbackDcr`,
`fallbackDce`, and `customTableCreate`. `controlledAlertParity` is planning
metadata only until a finite test window and complete batch fixture plan are
bound; `ownedResourceCleanup` is unsupported because there is no exact
run-owned deletion inventory or deletion executor. Do not invent CLI
component names or represent either as consented. Previous narrow DCR/DCE
consent does not imply ingestion, parity enablement, package acceptance, or
cleanup consent.

Authentication, Entra admin consent, role assignments, and permission
readiness are separate from both advance planning consent and final resource
write approval. None implies another.

### Package acceptance

Validate and optionally deploy `Package\mainTemplate.json` as a complete
solution package. For a partial package, V3.1 has already restricted that
template to the validated selected content; never repopulate it by scanning
excluded YAML.

- `DeployAnalyticsRule=true` selects Sentinel Analytic Rule content.
- `DeployCustomDetection=true` selects both Defender XDR Custom Detection
  installation and Content Hub registration, independently of Sentinel content.
  Both selections may be true. Use only parameters declared by the package.

Use ARM validation or preview only when supported for the selected resource
types and deployment features. Bicep extensibility imports do not support
`what-if` ([Microsoft Learn: unsupported deployment
features](https://learn.microsoft.com/en-us/graph/templates/limitations#unsupported-deployment-features));
do not pass or wait for a `what-if` result for that route. An ordinary ARM
preview cannot prove extension acceptance, and ARM validation does not validate
extension behavior. Registration support remains unverified; emitted templates
are not proof of live acceptance. The obsolete `RegisterE5Content` and
`E5Flavor` controls are not declared. Exact-scope approval must explicitly
include registration when selecting CDs. Existing instances are not disabled or
removed by these switches.

Before the write step, review the latest local Qualification
`deploymentPlanning` scope and explicitly persisted component-specific
planning consent. If the bound plan is unchanged, do not repeat the broad
planning question. Planning consent is not write authority. Immediately before
each bounded write operation or batch, show its exact scope and obtain fresh
explicit approval. A single approval may cover the enumerated resource/API
operations in that batch; it need not be repeated for every HTTP request.
Require a new approval if any operation expands beyond the batch. Missing or
stale planning consent, permissions, or successful preflight does not
substitute for the immediate gate.

### Repeatable rule deployment in a lab

Do not require a separate pre-deployment check for whether every Sentinel
Analytic Rule or Custom Detection already exists. For the same reviewed
identities and locked, approved non-production target, the Sentinel command
uses `PUT` on the deterministic alert-rule resource ID to create or update the
rule idempotently for the same ID and payload; rules remain disabled.
The alert-rule-template API is a catalog read surface, not a resource created
by this deployment command.

The current Graph deployer derives `xdr-<source-rule-GUID>` and internally
`GET`s that exact ID, `POST`s only when it is absent, or `PATCH`es when present,
then performs required read-back verification. This is repeatable at the
supported CLI workflow level for the reviewed ID; it is not a guarantee that
arbitrary Graph `POST` calls are idempotent. The separate
`preflight-deployment` exact-rule read is an optional diagnostic, not proof of
ownership or deployment readiness. The Graph deployment command still
requires its own `GET`; the current preflight also performs exact-ID reads and
can block on a denied read. These backend checks cannot be skipped by changing
instructions. Do not bypass them with direct API calls or blindly retry an
ambiguous write. If an existing ID has uncertain ownership or content, stop
for maintainer review rather than overwriting it.

This repeatability applies only to the exact reviewed solution content in the
locked approved lab, under the existing exact-scope approval, permission,
disabled-state, and verification gates. It does not authorize production
writes, changes to unrelated resources, or overwriting enabled or
unowned content.

### Alert-parity preparation

Deploy each selected reviewed pair disabled. For an applied partial package,
the deterministic deployment commands consume the selection-bound source and
Custom Detection lists, not every file in their folders:

```powershell
sentinel-xdr-migration deploy-analytic-rules `
  --solution "<solution-path>" `
  --workspace-resource-id "<workspace-arm-id>"

sentinel-xdr-migration deploy --solution "<solution-path>"
```

The first command writes
`Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\deployment.sentinel.json`. The
second writes
`Solutions\<solution>\Logs\sentinel-xdr-migration\<run-id>\deployment.graph.json`.

## Safety gates

Before any write:

1. Confirm the target is a non-production lab.
2. Show the subscription, resource group, workspace, tenant, solution, package
   version, mode, exact resource IDs, operation types, and count.
3. Immediately before the bounded operation/batch, require explicit approval
   for those exact values and the listed writes.
4. Confirm every Custom Detection YAML has `properties.status: disabled`.
5. Stop on unresolved conversion review, invalid KQL, missing entity mappings,
   duplicate IDs, or count mismatches within the exact selected scope. Excluded
   item failures remain separately reported and do not expand the deploy set.
6. Never infer permission from Entra Global Administrator. Verify Azure RBAC
   and Microsoft Graph Custom Detection scopes separately.
7. Ask before launching interactive authentication.

## Verification

Deployment passes only when:

- every requested ARM or Graph operation succeeds;
- deployed AR and CD IDs match the reviewed source manifest;
- every deployed rule is disabled;
- display names, queries, schedules, severities, tactics, and entity mappings
  match the generated artifacts; and
- the deployment reports contain no failed or silently skipped item.

If Graph read permission is unavailable, report verification as blocked even
when the write deployment reports success. Do not claim live status solely
from the source template.

Do not enable a rule in this skill. Rule enablement belongs exclusively to
`sentinel-xdr-alert-parity-validator`, which must disable every test rule on
completion or abort.
