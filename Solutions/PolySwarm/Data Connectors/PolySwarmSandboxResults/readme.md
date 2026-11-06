# PolySwarmSandboxResults

Shared infrastructure, not a data-connector-gallery tile a customer configures with
an API key. Deploys the Data Collection Endpoint, the `PolySwarmSandbox_CL` table and
the Data Collection Rule that every sandbox-detonating playbook writes one row to,
via the Azure Monitor Logs Ingestion API, once a detonation reaches a terminal state.
Deploy this once, before any sandbox playbook.

File: `azuredeploy.json`, a standalone ARM template (not a CCF `RestApiPoller`
four-file set, since nothing polls PolySwarm for this data).

## Why this exists instead of a CCF poller

An earlier design (`PolySwarmSandbox_CCF`) polled `/v3/sandbox/sandboxtask/my-tasks`
for completed detonations. Live testing against 42 real tasks in one account's history
showed the task list **never carries a verdict, malware family, ATT&CK techniques, or
network IOCs, for any task, regardless of status**; `report` is the literal empty
object `{}` on every row. The real verdict/family/ATT&CK data only exists behind
`/search/metadata/query`, keyed by sha256, and CCF's `RestApiPoller` cannot make a
second, per-row call to join the two. `my-tasks` also has no working time-window
filter (absolute or relative) and no completion-time field. A poller reading it could
never populate the columns that make the table useful, so the connector was deleted
and replaced with this shared infrastructure: each sandbox playbook already holds the
full result after polling its own submitted task to completion, so it POSTs a
finished row directly instead of a poller trying to reconstruct one from a thin list
endpoint.

## What it deploys

1. `Microsoft.Insights/dataCollectionEndpoints` (`polyswarm-dce`).
2. `Microsoft.OperationalInsights/workspaces/tables`, the `PolySwarmSandbox_CL` table,
   17 columns: `TimeGenerated (datetime), TaskId (string), ArtifactType (string),
   Sha256 (string), Url (string), FileName (string), Source (string), Provider
   (string), Community (string), Verdict (string), Score (real), Family (string),
   Techniques (dynamic), ReportUrl (string), CreatedAt (datetime), CompletedAt
   (datetime), IncidentArmId (string)`.
3. `Microsoft.Insights/dataCollectionRules` (`polyswarm-dcr-sandbox-results`), input
   stream `Custom-PolySwarmSandboxResults`, output stream
   `Custom-PolySwarmSandbox_CL`. The `transformKql` is a straight per-column cast
   (`tostring`/`todatetime`/`toreal`/`todynamic`), with no business logic: all the
   business logic (what the verdict is, which family, which techniques, when it
   completed) lives in the playbook that already polled the task to completion.

## Outputs

| Output | Used for |
| --- | --- |
| `dceLogsIngestionEndpoint` | The Logs Ingestion API endpoint each sandbox playbook posts to. |
| `dcrImmutableId` | The DCR's immutable id, part of the Logs Ingestion URL. |
| `dcrResourceId` | The DCR's full ARM resource id, used as the scope for each sandbox playbook's own Monitoring Metrics Publisher role assignment. Distinct from `dcrImmutableId`, which only the ingestion URL needs. |
| `streamName` | `Custom-PolySwarmSandboxResults`, the input stream name each playbook posts to. |

## Prerequisites

- A Microsoft Sentinel workspace (its Log Analytics workspace name and, optionally, a
  non-default location).
- Permission to deploy Log Analytics tables and Azure Monitor resources: Monitoring
  Contributor and Log Analytics Contributor at minimum; Owner or RBAC Administrator if
  you want the sandbox playbooks' automatic DCR role assignment to succeed at deploy
  time.

## Parameters

| Parameter | Notes |
| --- | --- |
| `log_analytics_workspace_name` | Required. The Log Analytics workspace backing your Sentinel instance. |
| `log_analytics_workspace_location` | Optional, defaults to the resource group's location. |

## Post-deployment steps

None beyond noting the four outputs above; there is nothing to authorize or role-grant
on this template itself. Each sandbox playbook you deploy afterward needs its own
**Monitoring Metrics Publisher** role assignment on `dcrResourceId` to write rows (see
`docs/permissions.md`); each playbook's template can create that assignment for
itself automatically at deployment.

## What a row looks like going in

Each sandbox playbook POSTs a JSON array (the Logs Ingestion API always wants an
array, even for one row) to:

```
POST {dceLogsIngestionEndpoint}/dataCollectionRules/{dcrImmutableId}/streams/Custom-PolySwarmSandboxResults?api-version=2023-01-01
```

Managed identity auth, audience `https://monitor.azure.com`, no key or secret. Row
keys match the table's column names exactly (see above). `Source` records which
playbook wrote the row (`Url`, `OutlookAttachment`, `StorageBlob`, `DefenderFile`).
`IncidentArmId` is the ARM resource id of the Sentinel incident the detonation ran
from, empty for a standalone submission.

## What needs Azure to confirm

The role-assignment `dependsOn`/`condition` ordering in each sandbox playbook's own
`Microsoft.Authorization/roleAssignments` resource (which references this template's
`dcrResourceId` output) has not been confirmed against a live deployment; that
resource lives in the playbooks, not in this template, so it is outside this
component's own files to test.

## Cross-reference with Analytic Rules

"PolySwarm sandbox detonation malicious" reads this table directly and declares its
dependency by borrowing the hunting connector's id
(`PolySwarmHuntingCCFDefinition`) with `dataType: PolySwarmSandbox_CL`, since this
component has no `dataConnectorDefinitions` resource of its own to point at (it is
plain infrastructure, not a CCF connector). See
`Data Connectors/PolySwarmHunting_CCF/readme.md`.
