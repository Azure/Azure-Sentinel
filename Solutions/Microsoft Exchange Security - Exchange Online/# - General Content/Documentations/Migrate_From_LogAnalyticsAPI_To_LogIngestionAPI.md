# Migrate from the Log Analytics HTTP Data Collector API to the Log Ingestion API

This guide describes how to migrate an existing Exchange Security Insights (ESI) deployment from the **legacy Log Analytics HTTP Data Collector API** (workspace ID + shared key) to the **Azure Monitor Log Ingestion API** (DCE + DCR + Entra ID identity).

> [!IMPORTANT]
> Microsoft has announced the retirement of the Log Analytics HTTP Data Collector API. All ESI deployments must switch to the Log Ingestion API before the end of support. New tables use `_CL` schemas with typed columns and are managed through Data Collection Rules (DCR).

## Why migrate

- The legacy API relies on the workspace shared key, which is a long-lived secret. The Log Ingestion API uses **Entra ID identities** (service principal with certificate or system-assigned **managed identity**).
- The Log Ingestion API supports **DCR-based transforms** — the ESI templates now use `parse_json` to extract typed sub-columns (for example the new `Identity_*` columns) directly at ingestion.
- Legacy tables are auto-provisioned with generic string columns; DCR-based tables have explicit typed schemas, enabling better queries, cost control, and retention management.
- The legacy API endpoint is **deprecated** and will stop accepting new data at end of support.

## Migration overview

The migration is a three-step process. You can perform all three steps back-to-back or spread them over multiple maintenance windows because the collector supports both APIs during the transition (`SentinelLogIngestionAPIActivated` toggle).

```text
Step 1                     Step 2                              Step 3
Upgrade script             Deploy Azure infrastructure         Update collector configuration
CollectExchSecIns.ps1  ->  DCE + DCRs + tables (ARM template)  ->  JSON / WinformConfig
(v8.0.0.0 or higher)       + role assignments
```

| Step | Duration       | Impact on production                                  |
|------|----------------|-------------------------------------------------------|
| 1    | Short          | None until the config file is switched (Step 3).      |
| 2    | Short          | None. New tables run in parallel with legacy tables.  |
| 3    | Short          | Ingestion path switches to the Log Ingestion API.     |

> [!TIP]
> Perform steps 1 and 2 in advance. Step 3 is the actual cutover and can be scheduled during a low-traffic window.

## Prerequisites

- Owner or Contributor on the target resource group.
- Access to the Log Analytics workspace hosting the current ESI tables.
- Ability to update the Automation Account `GlobalConfiguration` variable or the on-premises configuration file.
- (Recommended) Access to the [WinformConfig editor](./Migrate_From_LogAnalyticsAPI_To_LogIngestionAPI.md) to edit `CollectExchSecConfiguration.json` interactively.

## Step 1 — Upgrade the collector to v8.0.0.0 or higher

The **v8.0.0.0** release of `CollectExchSecIns.ps1` adds native support for the Log Ingestion API through the `SentinelLogIngestionAPIActivated` switch, DCE/DCR endpoint properties, certificate-based authentication, and managed identity for Azure Automation.

> [!IMPORTANT]
> Earlier versions of the collector only speak the legacy Log Analytics API. They cannot post to a DCE endpoint even if the configuration is updated. Upgrade the script **before** switching the configuration.

### Azure Automation runbook

1. Download the latest `CollectExchSecIns.ps1` (v8.0.0.0 or higher) from [the ESI script location](https://aka.ms/ESI-ExchangeCollector-Script).
2. Open the Automation Account, navigate to **Runbooks**, and select your ESI runbook.
3. Click **Edit** and replace the script content with the new version.
4. **Publish** the runbook.
5. Verify the runbook runs end-to-end with the existing (legacy) configuration. The behavior at this stage is unchanged — the collector still uses the legacy API because `SentinelLogIngestionAPIActivated` is still `false`.

### On-premises / hybrid collector (server or scheduled task)

1. Download the latest `CollectExchSecIns.ps1` (v8.0.0.0 or higher).
2. Replace the existing script file on the collector host (typical path: `C:\ESI\` or the location referenced by the scheduled task).
3. Run one manual execution to confirm the upgrade succeeded. Nothing else should change.

Once running v8.0.0.0, the collector emits a runtime warning banner whenever it still uses the legacy Log Analytics API, reminding operators to complete the migration. This banner disappears after Step 3.

## Step 2 — Deploy the Azure resources (DCE, DCRs, tables)

The ARM template `azuredeploy_ESI_LogIngestionAPI.json` provisions everything you need:

- 1 Data Collection Endpoint (DCE)
- Up to 3 custom Log Analytics tables (each optional):
  - `ESIAPIExchangeOnPremConfig_CL` — Exchange On-Premises configuration.
  - `ESIAPIExchangeOnlineConfig_CL` — Exchange Online configuration.
  - `ExchangeOnlineMessageTracking_CL` — Message tracking.
- Up to 3 Data Collection Rules (one per table).

> [!NOTE]
> The new tables live **alongside** the legacy `ESIExchangeConfig_CL` / `ExchangeOnlineMessageTracking_CL` tables. You can keep the legacy tables for historical queries or delete them after the migration.

### 2.1 Deploy the template

Deploy with Azure CLI, PowerShell, or the Azure Portal. Full instructions and parameter reference are in [README_LogIngestionAPI.md](./README_LogIngestionAPI.md).

Minimal PowerShell deployment (deploy everything, defaults):

```powershell
New-AzResourceGroupDeployment `
    -ResourceGroupName "rg-sentinel-esi" `
    -TemplateFile ".\ExchSecIns\Deployments\azuredeploy_ESI_LogIngestionAPI.json" `
    -workspaceName "law-sentinel-prod"
```

Deploy only the parts you need using the master switches:

- Online-only tenant: set `deployOnPremConfigTable=false`.
- On-premises only: set `deployOnlineConfigTable=false` and `deployMessageTrackingTable=false`.
- Reuse existing tables: set `deployTables=false`.

### 2.2 Collect the deployment outputs

Record these values — they go into the collector configuration in Step 3:

- `dataCollectionEndpointUri`
- `dataCollectionRuleOnPremisesConfigImmutableId` (if deployed)
- `dataCollectionRuleOnlineConfigImmutableId` (if deployed)
- `dataCollectionRuleMessageTrackingImmutableId` (if deployed)

### 2.3 Set up the ingestion identity

Choose one of the two authentication modes:

- **Entra ID application + certificate** — recommended for on-premises and server scenarios. Follow the full procedure in [README_AzureMonitorSetup.md](./README_AzureMonitorSetup.md#step-1-create-a-self-signed-certificate).
- **System-assigned managed identity** — recommended for Azure Automation runbooks. Enable the system-assigned identity on the Automation Account.

### 2.4 Assign the ingestion role

Grant **Monitoring Metrics Publisher** to the identity on **each DCR** it will send data to.

```powershell
$sp = Get-AzADServicePrincipal -ApplicationId "YOUR_APP_ID"   # or the Automation Account MI

New-AzRoleAssignment `
    -ObjectId $sp.Id `
    -RoleDefinitionName "Monitoring Metrics Publisher" `
    -Scope "/subscriptions/<sub>/resourceGroups/rg-sentinel-esi/providers/Microsoft.Insights/dataCollectionRules/DCR-ESI-OnlineConfig"
# Repeat for DCR-ESI-OnPremisesConfig and DCR-ESI-MessageTracking as needed.
```

> [!WARNING]
> Without this role assignment, the collector receives `403 Forbidden` from the Log Ingestion API. Verify the role is present before Step 3.

## Step 3 — Update the collector configuration

The configuration change is the actual cutover. Once `SentinelLogIngestionAPIActivated` is `true`, the collector stops calling the legacy API on its next execution and starts using the DCE/DCR endpoint.

### Option A — Update the configuration through the WinformConfig editor (recommended)

The WinformConfig GUI walks you through the relevant fields, hides legacy fields (`WorkspaceId`, `WorkspaceKey`) once `SentinelLogIngestionAPIActivated` is set, and validates the payload before saving.

1. From the ESI repository, open a PowerShell console and launch the editor:

   ```powershell
   pwsh -ExecutionPolicy Bypass `
     -File .\ExchSecIns\WinformConfig\SetupCollectExchSecConfiguration.ps1 `
     -ConfigPath .\ExchSecIns\CollectExchSecConfiguration.json
   ```

2. In the **Log Collection** section:
   - Set `SentinelLogIngestionAPIActivated` to `True`.
   - Fill `DataCollectionEndpointURI` with the DCE URI from Step 2.2.
   - Fill `DCRImmutableId` with the DCR immutable ID matching the table you target (Online, OnPremises, or MessageTracking).
   - Choose the authentication mode:
     - **Managed identity** (Azure Automation): set `UseManagedIdentity` to `True`.
     - **Certificate**: set `UseManagedIdentity` to `False`, then fill `TargetLogTenantID`, `TargetLogAppID`, and `TargetLogCertificateThumbprint`.
   - `WorkspaceId` and `WorkspaceKey` become hidden and can stay as-is (they are ignored once `SentinelLogIngestionAPIActivated` is `True`).
3. Review the **Raw JSON preview** and the **diff summary**.
4. Save the file. If the collector runs from Azure Automation, upload the new JSON to the `GlobalConfiguration` variable.

### Option B — Update the configuration file manually

Edit `CollectExchSecConfiguration.json` and update the `LogCollection` section:

```json
{
    "LogCollection": {
        "ActivateLogUpdloadToSentinel": "true",
        "SentinelLogIngestionAPIActivated": "true",
        "DataCollectionEndpointURI": "https://<dce-name>.<region>.ingest.monitor.azure.com",
        "DCRImmutableId": "dcr-00000000000000000000000000000000",
        "UseManagedIdentity": "false",
        "TargetLogTenantID": "<TENANT_ID>",
        "TargetLogAppID": "<APPLICATION_CLIENT_ID>",
        "TargetLogCertificateThumbprint": "<CERTIFICATE_THUMBPRINT>",
        "TargetLogAppSecretReference": "",
        "LogTypeName": "ESIExchangeConfig"
    }
}
```

Key rules:

- `SentinelLogIngestionAPIActivated` **must** be `"true"` (string).
- `DCRImmutableId` must correspond to the DCR routing to the target table (choose `OnPremisesConfigImmutableId`, `OnlineConfigImmutableId`, or `MessageTrackingImmutableId` from the deployment outputs).
- `LogTypeName` maps to the stream name (`Custom-<LogTypeName>` is sent to the DCR). Use `ESIExchangeConfig`, `ESIExchangeOnlineConfig`, or `ExchangeOnlineMessageTracking`.
- For Azure Automation with certificate auth, import the certificate into the Automation Account certificate store and populate `TargetLogAppSecretReference` with the automation variable name that stores the certificate reference.
- `WorkspaceId` / `WorkspaceKey` are no longer used; leave them empty or remove them for clarity.

### 3.1 Push the configuration

- **Azure Automation**: open the Automation Account, navigate to **Variables**, edit `GlobalConfiguration`, and paste the updated JSON. Publish any linked runbook if required.
- **Server-based collector**: replace the local `CollectExchSecConfiguration.json` used by the scheduled task or manual invocation.

### 3.2 Validate the cutover

1. Trigger a manual run of the collector.
2. Confirm the runtime log no longer displays the **legacy API warning banner** (see below).
3. Query the new tables in Log Analytics:

   ```kql
   ESIAPIExchangeOnlineConfig_CL
   | where TimeGenerated > ago(1h)
   | summarize count() by Section_s
   ```

4. Optional: query the legacy tables to confirm ingestion has stopped, then plan their decommissioning.

## Runtime warning banner (legacy API still in use)

Starting with v8.0.0.0, the collector displays a highly visible warning at the start of every execution when it detects the legacy Log Analytics API is still in use. Sample output:

```text
================================================================================
!! WARNING: Legacy Log Analytics HTTP Data Collector API is still in use.
!! The API is deprecated by Microsoft and will be retired.
!! Please migrate to the Azure Monitor Log Ingestion API before end of support.
!! Migration guide: ESI-PublicContent/Documentations/Migrate_From_LogAnalyticsAPI_To_LogIngestionAPI.md
================================================================================
```

The banner clears after Step 3 is applied and `SentinelLogIngestionAPIActivated` is `true` in the effective configuration.

## Post-migration housekeeping

- Remove the workspace shared key from any password vault / secure store used for the legacy configuration.
- Update any monitoring / alerts to point to the new `_CL` tables.
- Update Sentinel analytic rules, hunting queries, and workbooks that reference the legacy tables. New sub-columns such as `Identity_DistinguishedName_s` or `Identity_ObjectGuid_g` unlock queries that were not possible with the legacy schema.
- After a full retention cycle, plan the decommissioning of the legacy tables through the Log Analytics workspace UI.

## Rollback

If a critical issue is discovered, the transition is reversible:

1. Set `SentinelLogIngestionAPIActivated` back to `"false"` in `CollectExchSecConfiguration.json` (or via the WinformConfig editor).
2. Reinstate the legacy `WorkspaceId` / `WorkspaceKey` values.
3. Trigger the collector.

The collector will resume publishing to the legacy tables. The DCE, DCRs, and new tables remain in place for a later retry.

## Troubleshooting

| Symptom                                                                                              | Likely cause                                                          | Action                                                                                       |
|------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| The runtime banner still appears after step 3                                                        | Old configuration cached, or the runbook still uses the previous JSON | Re-check `SentinelLogIngestionAPIActivated`, republish the runbook.                          |
| HTTP 403 from the Log Ingestion API                                                                  | Missing role assignment on the DCR                                    | Assign **Monitoring Metrics Publisher** on the correct DCR.                                  |
| HTTP 400 `InvalidPayload`                                                                            | Column type mismatch or stream name mismatch                          | Verify `DCRImmutableId` and `LogTypeName` match the target DCR / stream.                     |
| No data in the new tables                                                                            | Wrong immutable ID (targets a different DCR)                          | Reconcile immutable IDs from the deployment outputs.                                         |
| Payload rejected `PayloadTooLarge`                                                                   | Segment > 1 MB                                                        | Lower `Advanced.MaximalSentinelPacketSizeMb` (default is `0.9` when the new API is enabled). |

## Related documentation

- ARM template and parameters: [README_LogIngestionAPI.md](./README_LogIngestionAPI.md)
- End-to-end Azure Monitor setup (Entra ID app, certificate, RBAC): [README_AzureMonitorSetup.md](./README_AzureMonitorSetup.md)
- WinformConfig editor: [ExchSecIns/WinformConfig/Readme.md](./WinformConfigReadme.md)
