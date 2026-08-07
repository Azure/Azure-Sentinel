# Exchange Security Insights - Log Ingestion API Deployment

This ARM template deploys the Azure infrastructure required for Exchange Security Insights (ESI) data collection using the **Azure Monitor Log Ingestion API** (the modern replacement for the deprecated Log Analytics HTTP Data Collector API).

> [!IMPORTANT]
> The legacy **Log Analytics HTTP Data Collector API** (workspace ID + shared key) is being retired by Microsoft. All new ESI deployments must use the Log Ingestion API. Existing deployments should migrate before the end-of-support date. See the migration guide: [Migrate_From_LogAnalyticsAPI_To_LogIngestionAPI.md](./Migrate_From_LogAnalyticsAPI_To_LogIngestionAPI.md).

## Resources Deployed

The template `azuredeploy_ESI_LogIngestionAPI.json` provisions the following resources into an **existing Log Analytics workspace**:

1. **Data Collection Endpoint (DCE)** — HTTPS endpoint receiving log payloads.
2. **Custom Log Analytics Tables** (each deployment is optional via master switches):
   - `ESIAPIExchangeOnPremConfig_CL` — Exchange **On-Premises** configuration data.
   - `ESIAPIExchangeOnlineConfig_CL` — Exchange **Online** configuration data.
   - `ExchangeOnlineMessageTracking_CL` — Message tracking logs.
3. **Data Collection Rules (DCR)** — one per table, defining schema, transform (`transformKql`), and routing:
   - `DCR-ESI-OnPremisesConfig`
   - `DCR-ESI-OnlineConfig`
   - `DCR-ESI-MessageTracking`

Each block is guarded by a boolean parameter so you can deploy the full stack or only a subset (for example, add on-premises collection to an existing online setup).

## Template Parameters

| Parameter                                 | Type    | Default                    | Purpose                                                                                                            |
|-------------------------------------------|---------|----------------------------|--------------------------------------------------------------------------------------------------------------------|
| `workspaceName`                           | string  | (required)                 | Name of the existing Log Analytics workspace (same subscription/resource group/region as the DCE).                 |
| `location`                                | string  | `resourceGroup().location` | Azure region for the DCE and DCRs. Must match the workspace region.                                                |
| `dataCollectionEndpointName`              | string  | `DCE-ESI-LogIngestion`     | Name of the DCE.                                                                                                   |
| `dataCollectionRuleOnPremisesConfigName`  | string  | `DCR-ESI-OnPremisesConfig` | Name of the on-premises config DCR.                                                                                |
| `dataCollectionRuleOnlineConfigName`      | string  | `DCR-ESI-OnlineConfig`     | Name of the Exchange Online config DCR.                                                                            |
| `dataCollectionRuleMessageTrackingName`   | string  | `DCR-ESI-MessageTracking`  | Name of the message tracking DCR.                                                                                  |
| `retentionInDays`                         | int     | `90` (min 30, max 730)     | Retention for the custom tables.                                                                                   |
| `deployTables`                            | bool    | `true`                     | Master switch — deploy the custom Log Analytics tables. Set to `false` when the tables already exist.              |
| `deployDataCollection`                    | bool    | `true`                     | Master switch — deploy the DCE and DCRs. Set to `false` to only (re)deploy the tables.                             |
| `deployOnPremConfigTable`                 | bool    | `true`                     | Deploy the on-premises config table and its DCR.                                                                   |
| `deployOnlineConfigTable`                 | bool    | `true`                     | Deploy the Exchange Online config table and its DCR.                                                               |
| `deployMessageTrackingTable`              | bool    | `true`                     | Deploy the message tracking table and its DCR.                                                                     |

> [!TIP]
> Use `deployTables=false` and `deployDataCollection=true` when reusing pre-existing tables (for example, after a schema-only redeployment). Use `deployTables=true` and `deployDataCollection=false` to only create or update table schemas.

## Prerequisites

- Azure subscription with **Contributor** (or higher) on the target resource group.
- An **existing Log Analytics workspace** (Microsoft Sentinel-enabled if you plan to detect on this data).
- Azure CLI or PowerShell with the `Az.*` modules.
- The Entra ID application (or managed identity) that will send data (see [README_AzureMonitorSetup.md](README_AzureMonitorSetup.md) for the full identity setup).

## Deployment

### Azure CLI

```bash
az login
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Create resource group (if needed)
az group create --name "rg-sentinel-esi" --location "eastus"

az deployment group create \
  --resource-group "rg-sentinel-esi" \
  --template-file azuredeploy_ESI_LogIngestionAPI.json \
  --parameters workspaceName=law-sentinel-prod
```

### PowerShell

```powershell
Connect-AzAccount
Set-AzContext -SubscriptionId "YOUR_SUBSCRIPTION_ID"

New-AzResourceGroup -Name "rg-sentinel-esi" -Location "eastus" -Force

New-AzResourceGroupDeployment `
  -ResourceGroupName "rg-sentinel-esi" `
  -TemplateFile "azuredeploy_ESI_LogIngestionAPI.json" `
  -workspaceName "law-sentinel-prod"
```

### Azure Portal

1. Navigate to **Deploy a custom template**.
2. Select **Build your own template in the editor**.
3. Paste the content of `azuredeploy_ESI_LogIngestionAPI.json`.
4. Fill in the parameters and confirm the master switches.
5. Click **Review + create**.

## Deployment Outputs

| Output name                                       | Purpose                                                        |
|---------------------------------------------------|----------------------------------------------------------------|
| `dataCollectionEndpointId`                        | Full resource ID of the DCE.                                   |
| `dataCollectionEndpointUri`                       | HTTPS ingestion URI. Required by the collector.                |
| `dataCollectionRuleOnPremisesConfigId`            | Full resource ID of the on-premises DCR.                       |
| `dataCollectionRuleOnPremisesConfigImmutableId`   | **Immutable ID** used by the collector for on-premises data.   |
| `dataCollectionRuleOnlineConfigId`                | Full resource ID of the online DCR.                            |
| `dataCollectionRuleOnlineConfigImmutableId`       | **Immutable ID** used by the collector for online data.        |
| `dataCollectionRuleMessageTrackingId`             | Full resource ID of the message tracking DCR.                  |
| `dataCollectionRuleMessageTrackingImmutableId`    | **Immutable ID** used by the collector for message tracking.   |
| `onPremConfigTableName`                           | Confirms the on-premises table name (or `Not deployed`).       |
| `configTableName`                                 | Confirms the Exchange Online table name (or `Not deployed`).   |
| `messageTrackingTableName`                        | Confirms the message tracking table name (or `Not deployed`).  |

Outputs of skipped resources return the string `Not deployed`.

Retrieve them after deployment:

```powershell
$deploy = Get-AzResourceGroupDeployment -ResourceGroupName "rg-sentinel-esi" -Name "YOUR_DEPLOYMENT_NAME"
$deploy.Outputs.dataCollectionEndpointUri.Value
$deploy.Outputs.dataCollectionRuleOnlineConfigImmutableId.Value
```

## Post-Deployment: Assign Ingestion Permissions

The identity used by the ESI collector needs the **Monitoring Metrics Publisher** role on **each DCR** it sends data to.

```bash
# Example: assign to a service principal on the Online Config DCR
az role assignment create \
  --role "Monitoring Metrics Publisher" \
  --assignee "YOUR_APP_OBJECT_ID" \
  --assignee-principal-type ServicePrincipal \
  --scope "/subscriptions/<sub>/resourceGroups/rg-sentinel-esi/providers/Microsoft.Insights/dataCollectionRules/DCR-ESI-OnlineConfig"
```

Repeat for `DCR-ESI-OnPremisesConfig` and `DCR-ESI-MessageTracking` as needed.

## Update the Collector Configuration

Update `CollectExchSecConfiguration.json` with the deployment outputs:

```json
{
  "LogCollection": {
    "ActivateLogUpdloadToSentinel": "true",
    "SentinelLogIngestionAPIActivated": "true",
    "DataCollectionEndpointURI": "<dataCollectionEndpointUri from outputs>",
    "DCRImmutableId": "<Immutable ID matching the target table>",
    "UseManagedIdentity": "false",
    "TargetLogTenantID": "YOUR_TENANT_ID",
    "TargetLogAppID": "YOUR_APP_ID",
    "TargetLogCertificateThumbprint": "YOUR_CERTIFICATE_THUMBPRINT",
    "LogTypeName": "ESIExchangeConfig"
  }
}
```

Pick the immutable ID matching the target table (on-premises, online, or message tracking).

## Table Schemas

Column suffixes follow Log Analytics conventions: `_s` string, `_d` real, `_g` guid, `_b` boolean, `_t` datetime, `_l` long, `_i` int.

### `ESIAPIExchangeOnPremConfig_CL` and `ESIAPIExchangeOnlineConfig_CL`

Both tables share the same schema (only the target audience differs).

| Column                          | Type     | Description                                            |
|---------------------------------|----------|--------------------------------------------------------|
| `TimeGenerated`                 | datetime | Ingestion timestamp (set by `transformKql`).           |
| `EntryDate_s`                   | string   | Date of the configuration entry.                       |
| `GenerationInstanceID_g`        | guid     | Unique identifier for the collector execution.         |
| `ESIEnvironment_s`              | string   | Exchange environment identifier.                       |
| `Section_s`                     | string   | Configuration section name.                            |
| `ExecutionResult_s`             | string   | Execution result (`Success`, `Error`, ...).            |
| `Identity_s`                    | string   | Raw serialized `Identity` object (source of truth).    |
| `Identity_Depth_d`              | real     | Depth of the identity in the directory hierarchy.      |
| `Identity_DistinguishedName_s`  | string   | Distinguished name (LDAP DN).                          |
| `Identity_DomainId_s`           | string   | Domain identifier (serialized when object).            |
| `Identity_IsDeleted_b`          | boolean  | Whether the identity is flagged as deleted.            |
| `Identity_IsRelativeDn_b`       | boolean  | Whether the DN is relative.                            |
| `Identity_Name_s`               | string   | Identity name.                                         |
| `Identity_ObjectGuid_g`         | guid     | Object GUID.                                           |
| `Identity_Parent_s`             | string   | Parent identity (serialized when object).              |
| `Identity_PartitionFQDN_s`      | string   | Partition FQDN.                                        |
| `Identity_PartitionGuid_g`      | guid     | Partition GUID.                                        |
| `Identity_Rdn_s`                | string   | Relative distinguished name (serialized when object).  |
| `IdentityString_s`              | string   | Human-readable identity string.                        |
| `RawData_s`                     | string   | Full raw configuration payload in JSON.                |
| `Name_s`                        | string   | Object name.                                           |
| `ProcessedByServer_s`           | string   | Server that produced the entry.                        |
| `PSCmdL_s`                      | string   | PowerShell cmdlet used to collect the entry.           |
| `WhenChanged_t`                 | datetime | `WhenChanged` timestamp.                               |
| `WhenCreated_t`                 | datetime | `WhenCreated` timestamp.                               |

> [!NOTE]
> The `Identity_*` sub-property columns are extracted from the source `Identity` object by the DCR's `transformKql` using `parse_json`. When `Identity` is `null` (some sections do not populate it), the sub-columns are `null`/empty — no ingestion error.

### `ExchangeOnlineMessageTracking_CL`

| Column                          | Type     | Description                                    |
|---------------------------------|----------|------------------------------------------------|
| `TimeGenerated`                 | datetime | Ingestion timestamp.                           |
| `schemaVersion_s`               | string   | Schema version of the log entry.               |
| `clientIp_s`                    | string   | Client IP address.                             |
| `clientHostname_s`              | string   | Client hostname.                               |
| `serverIp_s`                    | string   | Server IP address.                             |
| `senderHostname_s`              | string   | Sender hostname.                               |
| `sourceContext_s`               | string   | Source context.                                |
| `connectorId_s`                 | string   | Connector identifier.                          |
| `source_s`                      | string   | Message source.                                |
| `eventId_s`                     | string   | Event identifier.                              |
| `internalMessageId_s`           | string   | Internal message identifier.                   |
| `messageId_s`                   | string   | Message identifier.                            |
| `networkMessageId_s`            | string   | Network message identifier.                    |
| `recipientAddress_s`            | string   | Recipient email address.                       |
| `recipientStatus_s`             | string   | Recipient delivery status.                     |
| `totalBytes_l`                  | long     | Message size in bytes.                         |
| `recipientCount_i`              | int      | Number of recipients.                          |
| `relatedRecipientAddress_s`     | string   | Related recipient address.                     |
| `reference_s`                   | string   | Message reference.                             |
| `messageSubject_s`              | string   | Email subject line.                            |
| `senderAddress_s`               | string   | Sender email address.                          |
| `returnPath_s`                  | string   | Return path address.                           |
| `directionality_s`              | string   | Directionality (Originating / Incoming).       |
| `messageInfo_s`                 | string   | Additional message info.                       |
| `originalClientIp_s`            | string   | Original client IP.                            |
| `originalServerIp_s`            | string   | Original server IP.                            |
| `customData_s`                  | string   | Custom metadata.                               |
| `transportTrafficType_s`        | string   | Transport traffic type.                        |
| `FilePath_s`                    | string   | File path of the log entry.                    |
| `logId_s`                       | string   | Log identifier.                                |
| `messageTrackingTenantId_s`     | string   | Tenant identifier for the message tracking log.|

## Stream Names for API Ingestion

When calling the Log Ingestion API directly, the stream name that follows the DCR immutable ID must match the DCR:

| DCR                        | Stream declared                        | Output stream (table)                     |
|----------------------------|----------------------------------------|-------------------------------------------|
| `DCR-ESI-OnPremisesConfig` | `Custom-ESIExchangeConfig`             | `Custom-ESIAPIExchangeOnPremConfig_CL`    |
| `DCR-ESI-OnlineConfig`     | `Custom-ESIExchangeOnlineConfig`       | `Custom-ESIAPIExchangeOnlineConfig_CL`    |
| `DCR-ESI-MessageTracking`  | `Custom-ExchangeOnlineMessageTracking` | `Custom-ExchangeOnlineMessageTracking_CL` |

Example API call:

```powershell
$endpoint       = "https://<dce-name>.<region>.ingest.monitor.azure.com"
$dcrImmutableId = "dcr-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
$streamName     = "Custom-ESIExchangeOnlineConfig"

$uri = "$endpoint/dataCollectionRules/$dcrImmutableId/streams/$streamName" +
       "?api-version=2023-01-01"

Invoke-RestMethod -Uri $uri -Method Post -Body $jsonData -Headers @{
  "Authorization" = "Bearer $accessToken"
  "Content-Type"  = "application/json"
}
```

## Monitoring

Verify ingestion after deployment:

```kql
// Exchange Online configuration ingestion
ESIAPIExchangeOnlineConfig_CL
| summarize count() by bin(TimeGenerated, 1h), Section_s
| render timechart

// Exchange On-Premises configuration ingestion
ESIAPIExchangeOnPremConfig_CL
| summarize count() by bin(TimeGenerated, 1h), Section_s
| render timechart

// Message Tracking ingestion
ExchangeOnlineMessageTracking_CL
| summarize count() by bin(TimeGenerated, 1h), directionality_s
| render timechart
```

## Troubleshooting

### 403 Forbidden on ingestion

Verify the identity used by the collector has the **Monitoring Metrics Publisher** role on the correct DCR (not the DCE, not the workspace).

### Data does not appear

1. Confirm the `DCRImmutableId` in the collector configuration matches the DCR routing to the target table.
2. Check the `transformKql` output columns match the destination table columns.
3. Review collector logs for payload size errors (Log Ingestion API limit is 1 MB per call — the collector auto-segments).

### Table already exists

If a table already exists with a different schema, either:

- Redeploy with `deployTables=false` (leave tables as-is), or
- Manually align columns in the workspace, or
- Delete the table via the Log Analytics workspace and redeploy.

### Deployment fails on cross-region resources

The DCE, DCRs, and workspace must be in the **same region**. Adjust the `location` parameter or move the workspace.

## Cleanup

```bash
# Delete DCRs
az monitor data-collection rule delete --name "DCR-ESI-OnPremisesConfig" --resource-group "rg-sentinel-esi"
az monitor data-collection rule delete --name "DCR-ESI-OnlineConfig"     --resource-group "rg-sentinel-esi"
az monitor data-collection rule delete --name "DCR-ESI-MessageTracking"  --resource-group "rg-sentinel-esi"

# Delete DCE
az monitor data-collection endpoint delete --name "DCE-ESI-LogIngestion" --resource-group "rg-sentinel-esi"
```

> [!CAUTION]
> Custom Log Analytics tables cannot be deleted via API. They can only be removed through the Log Analytics workspace in the Azure Portal, or by deleting the workspace itself.

## Related Documentation

- Full identity + permission setup: [README_AzureMonitorSetup.md](README_AzureMonitorSetup.md)
- Migration from the legacy Log Analytics API: [Migrate_From_LogAnalyticsAPI_To_LogIngestionAPI.md](Migrate_From_LogAnalyticsAPI_To_LogIngestionAPI.md)
- Sample payload: [sample-Custom-ESIExchangeConfig.json](sample-Custom-ESIExchangeConfig.json)

## Support

- GitHub: <https://github.com/Azure/Azure-Sentinel>
- Microsoft Sentinel community: <https://techcommunity.microsoft.com/t5/microsoft-sentinel/bd-p/MicrosoftSentinel>
