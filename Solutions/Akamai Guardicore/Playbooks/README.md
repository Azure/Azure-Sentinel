# Guardicore Incident Enrichment

Author: Akamai Guardicore

This solution ships two Logic Apps that enrich Microsoft Sentinel incidents
with Guardicore connection data. When an incident is created, the trigger
playbook extracts IP entities, computes three 5-minute time slots around the
incident time, and writes slot manifest rows to Sentinel. A companion
recurrence-triggered runner Logic App polls a small Azure Storage Table for
due slots, fetches Guardicore `/api/v3.0/connections` for each slot's window
+ IP filter, and ingests the results to a second Sentinel custom log table.

There is **no Azure Function App** - both Logic Apps run natively. Ingestion
goes through a Data Collection Rule using the Logic Apps' system-assigned
managed identity; no workspace shared key is required.

## Quick deploy (recommended)

The single template `azuredeploy.json` at this folder bootstraps everything:
the Storage Account + work queue table, a Data Collection Endpoint (or
reuses an existing one), the Data Collection Rule, the two custom log
tables, both Logic Apps, and the role assignments. Click below, fill in the
form (workspace name + Guardicore credentials), and click **Create**.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAkamai%2520Guardicore%2FPlaybooks%2Fazuredeploy.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAkamai%2520Guardicore%2FPlaybooks%2FcreateUiDefinition.json)

[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAkamai%2520Guardicore%2FPlaybooks%2Fazuredeploy.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAkamai%2520Guardicore%2FPlaybooks%2FcreateUiDefinition.json)

The Deploy form has three steps:

1. **Sentinel workspace** - pick the workspace name (and its resource group
   if it's not the same as the deployment RG); optionally paste a resource
   ID for an existing Data Collection Endpoint to reuse.
2. **Guardicore credentials** - management URL (https only, regex-checked),
   service-account username, password (`securestring`).
3. **Advanced (optional)** - override default playbook / runner / storage
   account names. Leave blank for sensible defaults.

## Two manual steps after deploy

The portal can't fully automate two final touches. Both take ~30 seconds.

### 1. Authorize the Sentinel managed-API connection

The trigger playbook deploys a `Microsoft.Web/connections` resource for
`azuresentinel`, configured to authenticate as the playbook's
system-assigned managed identity. Azure requires a one-time interactive
"Authorize" click before the connection is usable.

1. Resource group -> find connection `azuresentinel-Guardicore-ProcessIncidentEnrichment`.
2. Edit API connection -> confirm **Authentication Type** is **Managed
   Identity** -> click **Authorize** -> **Save**.

If you skip this, every trigger run fails at the Sentinel webhook step
with `Unauthorized`.

### 2. Wire the playbook to a Sentinel automation rule

The trigger playbook only fires when a Sentinel automation rule routes an
incident to it.

1. Microsoft Sentinel -> workspace -> Configuration -> Automation.
2. **Create** -> **Automation rule**.
3. Name: `Guardicore: enrich on incident creation`. Trigger: **When
   incident is created**. Conditions: leave blank for "all incidents" or
   scope to severity / analytic rule.
4. Actions: **Run playbook** -> select `Guardicore-ProcessIncidentEnrichment`
   -> grant permissions when prompted.
5. Save.

If your Sentinel workspace lives in a different resource group than the
deployment, you may also need to grant the trigger playbook's managed
identity the **Microsoft Sentinel Responder** role on the workspace
(the consolidated template grants `Monitoring Metrics Publisher` on the
DCR and `Storage Account Contributor` on the storage account
automatically; the Sentinel role is workspace-scoped and the consolidated
template can't grant it cross-RG safely).

## Verify

Trigger a test incident with at least one IP entity and wait ~7 minutes
(5-minute slot wait + up to one 2-minute runner tick):

```kql
GuardicoreProcessedIncidents_CL
| where TimeGenerated > ago(15m)
| take 10
```

```kql
GuardicoreEnrichingConnections_CL
| where TimeGenerated > ago(15m)
| take 10
```

If either is empty after 15 minutes:
- Check Logic App run history for `Guardicore-ProcessIncidentEnrichment`
  and `Guardicore-EnrichmentRunner` for failed actions.
- Confirm the `Monitoring Metrics Publisher` role assignment is in place
  for both Logic App identities on the DCR (`<resource group> -> DCR ->
  Access control (IAM) -> Role assignments`).
- Inspect the `GuardicoreConnectionSlots` Azure Table for rows still in
  `pending` status (work waiting to be picked up).

## What gets deployed

| Resource | Purpose |
|---|---|
| `Microsoft.Storage/storageAccounts` | Hosts the work queue Azure Table. Auto-named (`stguardicore<unique>`) unless overridden. |
| `Microsoft.Storage/storageAccounts/tableServices/tables` | The `GuardicoreConnectionSlots` Azure Table itself. |
| `Microsoft.Insights/dataCollectionEndpoints` (conditional) | Logs Ingestion endpoint, created if no existing DCE supplied. |
| `Microsoft.Insights/dataCollectionRules` | Routes the two custom log streams into the workspace. |
| `Microsoft.OperationalInsights/workspaces/tables` x 2 | `GuardicoreProcessedIncidents_CL` + `GuardicoreEnrichingConnections_CL`. |
| `Microsoft.Web/connections` (azuresentinel) | Sentinel managed-API connection used by the trigger. |
| `Microsoft.Web/connections` (azuretables) | Storage tables managed-API connection shared by both Logic Apps. |
| `Microsoft.Logic/workflows` (trigger) | `Guardicore-ProcessIncidentEnrichment`, fires on Sentinel incident creation. |
| `Microsoft.Logic/workflows` (runner) | `Guardicore-EnrichmentRunner`, fires on a 2-minute recurrence. |
| `Microsoft.Authorization/roleAssignments` x 4 | DCR + Storage RBAC for both Logic App managed identities. |

## What changed in v3.1.0

- The Function App at `Playbooks/CustomConnector/` was removed - there is
  no Python code anywhere on the playbook side.
- The legacy `Playbooks/azuredeploy.json` (which deployed the legacy
  playbook only) was replaced by the new consolidated `azuredeploy.json`
  that deploys everything.
- The two Sentinel custom log tables (`GuardicoreProcessedIncidents_CL`,
  `GuardicoreEnrichingConnections_CL`) keep the same names but are now
  DCR-based from the start.
- The legacy `FunctionAppName` ARM parameter is gone.

This is a **greenfield release** - no migration path is provided for v1
deployments. If a v1 deployment exists in your tenant, uninstall it
first.

## Deploying individual components (for power users)

The five per-component templates are still in this tree and can be
deployed individually if you have a custom orchestration:

- `AkamaiGuardicoreEnrichment_dcr/AkamaiGuardicoreEnrichment_Storage.json`
- `AkamaiGuardicoreEnrichment_dcr/AkamaiGuardicoreEnrichment_DCR.json`
- `AkamaiGuardicoreEnrichment_dcr/AkamaiGuardicoreEnrichment_Tables.json`
- `Guardicore-ProcessIncidentEnrichment/azuredeploy.json`
- `Guardicore-EnrichmentRunner/azuredeploy.json`

See the per-component runbook at
`.a5c/runs/01KQ4NG4762ZPTJH1BRKS9X7KK/artifacts/production-deployment-runbook.md`
for the manual deploy order and parameter wiring.

## Citations

- [Sentinel playbook recommendations](https://learn.microsoft.com/en-us/azure/sentinel/playbook-recommendations)
- [Logic Apps native HTTP action](https://learn.microsoft.com/en-us/azure/logic-apps/connectors/connectors-native-http)
- [Logic Apps managed identity authentication](https://learn.microsoft.com/en-us/azure/logic-apps/authenticate-with-managed-identity)
- [Logs Ingestion API](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview)
- [DCR transform structure](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/data-collection-transformations-structure)
- [Logic Apps recurrence trigger](https://learn.microsoft.com/en-us/azure/connectors/connectors-native-recurrence)
- [Sentinel automation rules](https://learn.microsoft.com/en-us/azure/sentinel/automate-incident-handling-with-automation-rules)
