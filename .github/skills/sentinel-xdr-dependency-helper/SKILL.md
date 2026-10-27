---
name: sentinel-xdr-dependency-helper
description: Help authors review and fill XDR YAML workload and connector dependencies using exact-query Log Analytics lab metadata. Conversion remains offline.
---

# Review detection dependency provenance

For workbook gaps, use the same explicit accept/change/defer experience with
individual query pointers and hashes. Workbook proposals/configuration are
separate from the detection-only `dependency-plan` command. Static/manual review
starts with `workbook-dependency-plan --solution "<path>" --run-id "<run-id>"`.
Use `workbook-review` with `--plan`, `--decisions`, `--plan-sha256`, `--actor`,
`--reference`, and a new run-local `--output-dir` to emit reviewed conversion
configuration and a receipt. These commands do not edit source content or
authenticate. A reviewed removal request is a pending parser-change action,
not proof of an applied removal. `convert --overwrite-workbooks` can replace
unchanged hash-bound managed workbook drafts without authorizing detection
overwrites. Static/manual review
and explicitly approved lab metadata discovery are available in either profile.
Do not execute unresolved workbook parameters or reuse detection consent for
workbook queries. Show underlying data types, workload mappings, connector
alternatives, function prerequisites, and all remaining technical failures.
Prefer modern connectors over deprecated alternatives only with reviewed
recommendation/lifecycle evidence. Never require both by default.

Reviewed Sentinel workspace functions can be preserved for workbooks and AH,
not Custom Detections. Standard built-in ASIM parsers starting with `_` (such
as `_ASim_*` and `_Im_*`) are accepted by Defender XDR Advanced Hunting and can
be used in both Custom Detections and Defender Workbooks; do not reject them as
unsupported workspace-saved functions. Keep exact packaged function-definition
hashes in `contentProvenance.requiredWorkspaceFunctions`; function aliases are
not tables.
`_GetWatchlist` is a supported built-in in Sentinel/AH; do not surface it as a
missing parser or add saved-search installation dependencies for it.
`Watchlist` is platform reference data, not a connector-fed telemetry data type.
Preserve raw lineage but exclude it from required workload/connector data types;
do not ask the user to choose a connector for it.
Required parsers must be installed before the workbook. Optional vendor branches
can remain unavailable with explicit warnings and incomplete coverage. Offer
keep/remove/defer; removal needs a scoped parser-change preview and approval,
not deletion of shared functions or automatic clearance of technical blockers.

Use this skill when YAML prerequisites are missing or uncertain, or when a user
requests lab-assisted dependency validation. This is a validation helper, not
deployment, ingestion, qualification, or permission to change toolkit code.

## Offline proposal

Run `sentinel-xdr-migration dependency-plan --solution "<solution-path>"`.
It reads the original Sentinel queries, converted queries, source connector
declarations, and current table mappings. It makes no Azure call and does not
modify YAML.
Conversion never requires Log Analytics authentication or availability.

Inspect each proposal and unresolved reason. The workload vocabulary is:
`mde`, `mdo`, `mdi`, `mda`, `mdc`, `entraid`, `purview`, `appgovernance`,
`sentinel`, `mtp`. These are toolkit telemetry prerequisites, not Graph
`serviceSource` values or a claimed public contentProvenance API enum.
Only independently reviewed mappings are built in. Do not copy private catalogs.
In particular, `SecurityAlert` does not establish a specific Defender product
or connector. Preserve authoritative source connector declarations.

## Approved lab metadata

For Authoring or Qualification, ask for explicit bounded read-only approval
covering the exact original queries, tenant, subscription, and lab workspace
before executing them. Use the existing locked target in Qualification;
Authoring requires an explicitly selected lab. Do not reinterpret existing
Advanced Hunting consent as Sentinel-query permission. No authentication,
permission changes, environment writes, or Qualification gates are authorized.

Inspect advertised official Sentinel Triage MCP tools first. Use one only if
it can request `Prefer: include-dataSources=true` and return input metadata.
If that capability is absent or the provider fails, use the Azure CLI runner
skill for the approved Log Analytics REST query:

```text
POST https://api.loganalytics.io/v1/workspaces/<workspace-id>/query
Prefer: include-dataSources=true
Content-Type: application/json
{"query": "<exact sentinelQuery from dependency-plan>"}
```

Use a run-local JSON body file, not shell interpolation of KQL. Run only against
the approved workspace with an already authenticated identity verified against
the approved tenant/subscription. Do not sign in automatically. Do not replace
the original query with `getschema`, add a time range, or otherwise change it.
Do not fall back after a genuine KQL failure, partial result, auth failure from
the direct provider, or any failed REST response. Record the failure explicitly.

The SDK source-validation runner also requests input metadata, but its existing
Qualification target and consent gates remain unchanged.

Keep raw successful metadata and provider/target evidence in ignored run-local
files. Normalize one result per detection:

```json
{
  "results": [{
    "detection": "Example.yaml",
    "status": "passed",
    "workspaceId": "<approved workspace customer GUID>",
    "querySha256": "<sentinelQuerySha256 from the plan>",
    "dataSources": [{"tables": [{"name": "DeviceEvents"}]}],
    "error": null
  }]
}
```

Never use response `tables` (output rows/schema) as input lineage. Import the
complete current family with:

```text
sentinel-xdr-migration dependency-plan --solution "<solution-path>" --results "<metadata.json>" --workspace-id "<approved-workspace-id>"
```

The backend accepts 1-10 distinct underlying tables. More than 10, or missing/
empty metadata from a successful query, triggers the conservative scanner.
It records the method, fallback reason, original table list and query hash.
It also scans the converted query for added table references and reports
`targetDataTypes` and `targetDiscoveryMethod`. Source API metadata is not a
claim that Graph returned input lineage for the converted query.
Malformed metadata and failed/stale/cross-workspace results are errors, not
successful empty dependency lists.

## Review and YAML update

Present proposed records, fallback use, unknown mappings, and live comparison
errors. Ask the user to supply unresolved data types, workload mappings and
connectors. If nothing resolves, leave arrays empty and explicitly mark the
provenance `dependencyReviewRequired: true`; never describe it as verified.
Native XDR rules can legitimately have no Sentinel connector prerequisite.
Reviewed no-prerequisite arrays are valid; unknown empty arrays are not a
review decision.

After explicit approval, update only the detection YAML's
`contentProvenance.requiredWorkloads` and
`contentProvenance.requiredDataConnectors`, preserving `source`, `conversion`,
identities, versions, source rule bytes, tactics and disabled status. Clear
`dependencyReviewRequired` only after the missing information is reviewed.
Records have the following form:

```yaml
contentProvenance:
  requiredWorkloads:
    - workload: mde
      dataTypes: [DeviceEvents]
  requiredDataConnectors:
    - connectorId: MicrosoftThreatProtection
      dataTypes: [DeviceEvents]
```

Do not add packageId/packageVersion/contentId/contentVersion to authored YAML.
Packaging derives them from solution metadata and the canonical detection
identity/version. Dependencies belong to the full Content Hub record, not the
lightweight deployed rule record.

Run offline `validate`, then repeat the imported lab comparison when applicable.
Retain evidence tied to the exact query and current declarations. YAML edits
invalidate previous package/validation evidence. Metadata verifies table
prerequisites, not connector installation or availability, alert parity,
marketplace registration, or public Graph support for contentProvenance.
