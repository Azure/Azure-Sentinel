# Akamai Guardicore Connector - v3.0.0 Migration Guide

## Overview

Version 3.0.0 of the Akamai Guardicore solution migrates the data connector from an
Azure Functions-based implementation to the Microsoft Sentinel
[Codeless Connector Framework (CCF/CCP)](https://learn.microsoft.com/en-us/azure/sentinel/create-codeless-connector).

**What changed**

- The connector is no longer backed by an Azure Function App. Polling, pagination,
  authentication, and ingestion are all performed by the platform-native CCF runtime.
- No Function App to deploy, scale, monitor, or patch.
- Workspace shared-key (`sharedKeys`) permission is no longer required by the connector.
- Credentials are configured directly on the connector tile in Sentinel.

**What is preserved**

- Table names are unchanged: `GuardicoreAgents_CL`, `GuardicoreAssets_CL`,
  `GuardicoreApplications_CL`, `GuardicorePolicyRules_CL`.
- Bundled workbooks, analytics rules, and playbooks continue to operate against
  these tables and require no changes.

## Prerequisites

- A Microsoft Sentinel-enabled Log Analytics workspace.
- The Guardicore Centra management URL (e.g. `https://<your-tenant>.cloud.guardicore.com`).
- A Guardicore service-account username and password with the **Read-only** role,
  authorized for the following endpoints:
  - `POST /api/v3.0/authenticate`
  - `GET  /api/v3.0/agents`
  - `GET  /api/v3.0/assets`
  - `GET  /api/v3.0/workflow/projects`
  - `GET  /api/v3.0/visibility/policy/rules`
- Azure CLI 2.61.0 or newer with the `log-analytics` extension installed (for the
  table migration step below).

## Upgrade Path for Existing Customers (One-Way)

> **Important:** This is a one-way migration. Once a `_CL` table is migrated from
> the legacy Custom Logs (DCR-less) type to DCR-based, it cannot be reverted.
> Read the [Reversibility / rollback](#reversibility--rollback) section before
> beginning.

1. **Stop the existing v1 Function App connector.** In the Azure portal, navigate
   to the Guardicore Function App and stop it. This halts ingestion from the
   legacy path.

2. **Wait approximately 5 minutes** for any in-flight queue items / HTTP Data
   Collector batches to drain into the workspace.

3. **Migrate each of the four Guardicore tables** from Custom Logs (DCR-less) to
   DCR-based using `az monitor log-analytics workspace table migrate`. See the
   Microsoft Learn guidance:
   <https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate>.

   Run this command once per table, substituting the table name:

   ```bash
   az monitor log-analytics workspace table migrate \
     --resource-group <rg> \
     --workspace-name <workspace> \
     --name GuardicoreAgents_CL
   ```

   Tables to migrate:

   - `GuardicoreAgents_CL`
   - `GuardicoreAssets_CL`
   - `GuardicoreApplications_CL`
   - `GuardicorePolicyRules_CL`

4. **Verify each table's type** is now DCR-based:

   ```bash
   az monitor log-analytics workspace table show \
     --resource-group <rg> \
     --workspace-name <workspace> \
     --name GuardicoreAgents_CL \
     --query "tableType"
   ```

   Expected output: `DataCollectionRuleBased`.

5. **Deploy the v3.0.0 solution** from the Microsoft Sentinel Content Hub
   ("Akamai Guardicore"). Accept the deployment into the same workspace.

6. **Configure CCF credentials on the connector tile.** Open the
   *Akamai Guardicore (CCP)* data connector and provide:
   - **Guardicore Management URL** (e.g. `https://<tenant>.cloud.guardicore.com`)
   - **Username**
   - **Password**

   Click *Connect*. The CCF runtime will begin polling the five endpoints listed
   in [Prerequisites](#prerequisites).

7. **Verify ingestion** approximately 15 minutes after connecting. For each table:

   ```kusto
   GuardicoreAgents_CL | where TimeGenerated > ago(15m) | take 10
   ```

   Repeat for `GuardicoreAssets_CL`, `GuardicoreApplications_CL`, and
   `GuardicorePolicyRules_CL`.

8. **After 24 hours of clean ingestion**, delete the old Function App and any
   leftover deployment artifacts (storage account used for Function state, App
   Service plan, Application Insights resource if dedicated, and any Key Vault
   secrets that held the workspace shared key or Guardicore credentials for the
   old connector).

## Reversibility / Rollback

The `az monitor log-analytics workspace table migrate` operation is **not
reversible**. Once a table is converted to DCR-based, there is no supported path
back to the legacy Custom Logs (DCR-less) type.

If you encounter ingestion problems after cutover:

- **Do not** attempt to roll back the table migration.
- **Do not** redeploy the v1 Function App against the migrated tables.
- Open a Microsoft support ticket referencing the migrated table(s) and the v3.0.0
  CCF connector, and an Akamai Guardicore support ticket if Guardicore-side
  authentication or API behavior is suspect.

To minimize risk, exercise the upgrade in a non-production workspace first if
one is available.

## CCF Overview

The Codeless Connector Framework (also referred to as CCP, the Codeless
Connector Platform) lets connector authors describe polling-based ingestion
declaratively in JSON, removing the need for connector-specific compute. See
the Microsoft Learn reference:
<https://learn.microsoft.com/en-us/azure/sentinel/create-codeless-connector>.

## Permission Changes

The v3.0.0 solution drops the following permissions previously required by v1:

- `Microsoft.OperationalInsights/workspaces/sharedKeys/action` - the workspace
  shared key was used by the Function App to write via the legacy HTTP Data
  Collector API. CCF uses the Logs Ingestion API via a managed Data Collection
  Rule and Data Collection Endpoint, so the shared key is no longer required.
- `Microsoft.Web/sites/*` (Function App deployment) - no Function App is
  deployed by v3.0.0.

The connector retains only standard Read / Write / Delete permissions on
`Microsoft.OperationalInsights/workspaces` for table and DCR management.
