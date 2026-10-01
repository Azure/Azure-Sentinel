# Configure the Exchange Security Insights Online Collector with Azure Monitor

## Overview

The **Exchange Security Insights Online Collector (Azure Monitor)** data connector and the Azure Automation deployment template configure the resources required to collect Exchange Online security configuration data through the Azure Monitor Log Ingestion API.

The deployment uses the **system-assigned managed identity of the Azure Automation account**. The Online collector does not require a local certificate, an application secret, or a Windows scheduled task.

The deployment has two parts:

1. The data connector deploys the Log Analytics table, Data Collection Endpoint (DCE), and Data Collection Rule (DCR).
2. The Azure Automation template deploys the Automation account, managed identity, modules, runbook, daily schedule, configuration variables, and the managed identity role assignment on the DCR.



## Resources deployed

### Data connector resources

The data connector deploys:

- The `ESIAPIExchangeOnlineConfig_CL` custom Log Analytics table.
- The DCE.
- The DCR.

### Azure Automation resources

The Azure Automation template deploys or updates:

- An Azure Automation account with a system-assigned managed identity.
- The `ExchangeOnlineManagement` module.
- `Microsoft.Graph.Authentication`.
- `Microsoft.Graph.Users`.
- `Microsoft.Graph.Groups`.
- The `Start-ESICollector` PowerShell 5.1 runbook.
- The `ESIConfig-Each-day` daily schedule.
- The runbook schedule association.
- The `GlobalConfiguration`, `TenantName`, and `LastDateTracking` Automation variables.
- The **Monitoring Metrics Publisher** role assignment for the Automation account managed identity on the DCR.

## Prerequisites

Before starting, verify that:

- The **Microsoft Exchange Security for Exchange Online** solution is installed in Microsoft Sentinel.
- You have sufficient permissions to configure the data connector and deploy its resources.
- You can deploy an Azure Automation account and assign an Azure role on the DCR.
- You have chosen a generic environment display name for the Microsoft Sentinel workbooks, for example `Production`. The template adds the `-Cloud` suffix when it is not already present.
- A Global Administrator can run the permission assignment script and grant admin consent.

For the complete permission requirements, see [Exchange Security Insights Collector for Exchange Online](./ESICollector.md).

## Choose the appropriate scenario

### New deployment

1. Install the **Microsoft Exchange Security for Exchange Online** solution from Microsoft Sentinel Content Hub.
2. Open **Data connectors** in Microsoft Sentinel.
3. Select **Exchange Security Insights Online Collector (Azure Monitor)**.
4. Open the connector page and select **Deploy Exchange Collector Push connector resources**.
5. Wait for the data connector deployment to complete.
6. Record the tenant ID, DCE URI, DCR immutable ID, and stream name displayed on the connector page. Retrieve the DCR name from its immutable ID (see [Retrieve the DCR name](#retrieve-the-dcr-name)).
7. Use the **Deploy to Azure** action on the connector page to deploy and configure the Automation account.
8. Provide the Automation account name, generic environment display name, tenant ID, DCE URI, DCR immutable ID, and DCR name.
9. Wait for the Automation deployment to complete.
10. [Assign the Microsoft Graph and Exchange Online permissions](#assign-microsoft-graph-and-exchange-online-permissions) to the Automation account managed identity.
11. [Assign the **Global Reader** or **Security Reader** Microsoft Entra role](#assign-a-microsoft-entra-directory-role) to the managed identity.
12. Run the `Start-ESICollector` runbook manually and verify ingestion before relying on the daily schedule.

### Upgrade an existing deployment

1. Update the **Microsoft Exchange Security for Exchange Online** solution from Microsoft Sentinel Content Hub.
2. Open **Data connectors** in Microsoft Sentinel.
3. Select **Exchange Security Insights Online Collector (Azure Monitor)**.
4. Select **Deploy Exchange Collector Push connector resources** and wait for completion.
5. Record the DCE URI and DCR immutable ID displayed by the connector. Retrieve the DCR name from its immutable ID (see [Retrieve the DCR name](#retrieve-the-dcr-name)).
6. Update the existing runbook and `GlobalConfiguration` variable by following [Update an existing Azure Automation deployment](#update-an-existing-azure-automation-deployment).
7. Verify that the `Start-ESICollector` runbook, modules, `GlobalConfiguration` variable, and daily schedule are configured correctly.
8. Verify that the Automation account managed identity has **Monitoring Metrics Publisher** on the DCR.
9. If the managed identity was recreated, [assign the Microsoft Graph and Exchange Online permissions](#assign-microsoft-graph-and-exchange-online-permissions) and the [Microsoft Entra directory role](#assign-a-microsoft-entra-directory-role) again.
10. Run the runbook manually and verify ingestion before relying on the schedule.

## Update an existing Azure Automation deployment

> [!IMPORTANT]
> Do not use **Deploy to Azure** as the standard update method for an existing Automation account. The current template generates a new job schedule association identifier during each deployment and uses a fixed runbook content version. A redeployment has not been validated as an idempotent update path.

Update the existing Automation account manually:

1. Back up the existing `GlobalConfiguration` variable.
2. Open the `Start-ESICollector` runbook in the Automation account.
3. Replace the runbook content with the latest `CollectExchSecIns.ps1` content.
4. Save and publish the runbook.
5. Update the existing `GlobalConfiguration` variable while preserving all unrelated settings.
6. Set or update:
   - `SentinelLogIngestionAPIActivated` to `true`.
   - `DataCollectionEndpointURI` to the DCE URI displayed by the connector.
   - `DCRImmutableId` to the immutable ID displayed by the connector.
   - `UseManagedIdentity` to `true`.
   - `TargetLogTenantID` to the Microsoft Entra tenant ID.
   - `LogTypeName` to `ESIExchangeOnlineConfig`.
7. Verify that the required PowerShell 5.1 modules are installed.
8. Verify that the Automation account managed identity has **Monitoring Metrics Publisher** on the DCR.
9. Verify that the existing daily schedule remains enabled and linked to `Start-ESICollector`.

After the update, run `Start-ESICollector` manually and verify ingestion.

## Values provided by the data connector

The connector page displays:

- Tenant ID (Directory ID).
- Data Collection Endpoint URI.
- Data Collection Rule immutable ID.
- Stream name: `Custom-ESIExchangeOnlineConfig`.

The environment display name is not supplied by the connector. Choose a generic name that identifies the environment in the workbooks, for example `Production`. The Automation deployment stores it as `Production-Cloud`.

### Retrieve the DCR name

The connector provides the DCR immutable ID but does not display the DCR resource name required by the Azure Automation template.

In the Azure portal:

1. Open the resource group containing the connector resources.
2. Filter the resources by type **Data Collection Rule**.
3. Open the DCR whose immutable ID matches the value displayed by the connector.
4. Copy the resource name from the DCR **Overview** page.

Alternatively, from a PowerShell session with the `Az.Monitor` module, connect to the correct subscription and run:

```powershell
$resourceGroupName = "<resource-group-containing-the-DCR>"
$dcrImmutableId = "<dcr-immutable-id-displayed-by-the-connector>"

$dcr = Get-AzDataCollectionRule -ResourceGroupName $resourceGroupName |
    Where-Object { $_.ImmutableId -eq $dcrImmutableId }

if (-not $dcr) {
    throw "No DCR with immutable ID '$dcrImmutableId' was found in resource group '$resourceGroupName'."
}

$dcr | Select-Object Name, ImmutableId, Id
```

Use the value in the `Name` column for the `dcrName` deployment parameter. If no result is returned, verify the active subscription, resource group, and immutable ID.

Use these values when deploying the Azure Automation template.

## Managed identity configuration

The Automation template generates the `GlobalConfiguration` variable with the following Azure Monitor settings:

```json
{
  "LogCollection": {
    "ActivateLogUpdloadToSentinel": "true",
    "LogTypeName": "ESIExchangeOnlineConfig",
    "SentinelLogIngestionAPIActivated": "true",
    "DataCollectionEndpointURI": "<value displayed by the data connector>",
    "DCRImmutableId": "<value displayed by the data connector>",
    "UseManagedIdentity": "true",
    "TargetLogTenantID": "<tenant ID>"
  }
}
```

This is a partial example. Do not replace the complete `GlobalConfiguration` value with this example.

When the Log Ingestion API is enabled:

- `WorkspaceId` and `WorkspaceKey` are legacy settings and are not used for ingestion.
- `UseManagedIdentity` must remain `true`.
- `DataCollectionEndpointURI` must match the DCE displayed by the connector.
- `DCRImmutableId` must match the DCR displayed by the connector.
- `LogTypeName` must remain `ESIExchangeOnlineConfig`.

## Assign Microsoft Graph and Exchange Online permissions

The Automation deployment creates the managed identity but does not assign the Microsoft Graph or Exchange Online application permissions required by the collector.

Use [`ExchangeOnlinePermSetup.ps1`](../Solutions/ESICollector/OnlineDeployment/ExchangeOnlinePermSetup.ps1).

### Run the permission script

Run the script from a workstation where `Microsoft.Graph.Authentication` and `Microsoft.Graph.Applications` are installed. Use a **Global Administrator** account and grant admin consent for:

- `AppRoleAssignment.ReadWrite.All`
- `Application.Read.All`

Retrieve the managed identity object ID from **Automation account** > **Account Settings** > **Identity**, and then run:

```powershell
.\ExchangeOnlinePermSetup.ps1 `
    -MIIDParam "<managed-identity-object-id>" `
    -TenantId "<tenant-id>" `
    -InteractiveAuth
```

Omit `InteractiveAuth` to use device authentication.

The script assigns:

- `Group.Read.All`
- `User.Read.All`
- `AuditLog.Read.All`
- `Exchange.ManageAsApp`

### Assign a Microsoft Entra directory role

The script does not assign a directory role. Assign at least **Global Reader** or **Security Reader** to the Automation account managed identity.

For more information, see [Assign Microsoft Entra roles to the application](https://learn.microsoft.com/powershell/exchange/app-only-auth-powershell-v2?view=exchange-ps#assign-microsoft-entra-roles-to-the-application).

## Validate the deployment

### Verify Azure Automation

Confirm that:

- The Automation account has a system-assigned managed identity.
- The required PowerShell 5.1 modules are available.
- The `Start-ESICollector` runbook is published.
- The `ESIConfig-Each-day` schedule is enabled and linked to the runbook.
- `GlobalConfiguration`, `TenantName`, and `LastDateTracking` exist.
- The managed identity has **Monitoring Metrics Publisher** on the DCR.

### Run the collector

Start the `Start-ESICollector` runbook manually. Confirm that the job completes without authentication, permission, or ingestion errors.

Then run:

```kql
ESIAPIExchangeOnlineConfig_CL
| summarize Entries = count(), LastIngestion = max(TimeGenerated)
    by GenerationInstanceID_g, ESIEnvironment_s
| order by LastIngestion desc
```

The data connector status should change to **Connected** after data is received.

## Data destination

| Component | Value |
|-----------|-------|
| Table | `ESIAPIExchangeOnlineConfig_CL` |
| Stream | `Custom-ESIExchangeOnlineConfig` |
| Collector `LogTypeName` | `ESIExchangeOnlineConfig` |

The DCR transform extracts the `Identity_*` columns from the source `Identity` object. The original `Identity_s` column is preserved for compatibility with existing analytics, hunting queries, and workbooks.

## After upgrading an existing deployment

### Post-migration cleanup

After several successful scheduled executions:

1. Keep the backed-up legacy `GlobalConfiguration` value for the agreed rollback period.
2. Remove the legacy workspace key from Automation variables or other secure stores after the rollback period.
3. Update custom analytics, hunting queries, or workbooks that directly reference `ESIExchangeOnlineConfig_CL`.
4. Retain the legacy table for historical data until its retention period expires.

Do not delete the Automation account, managed identity, DCE, DCR, or new table while the collector uses the Log Ingestion API.

### Rollback during validation

Rollback is intended only for the validation period and only while the legacy API remains available.

1. Disable the `ESIConfig-Each-day` schedule.
2. Restore the backed-up `GlobalConfiguration` value.
3. Confirm that `SentinelLogIngestionAPIActivated` is set to `false`.
4. Run `Start-ESICollector` manually.
5. Verify that data appears in the legacy table.
6. Re-enable the schedule.

The Azure Monitor resources can remain deployed while the migration issue is investigated.

## Troubleshooting

### The Azure Monitor connector is not available

Confirm that the Microsoft Exchange Security for Exchange Online solution was installed or updated successfully in Content Hub.

### The Automation deployment fails

Verify:

- The tenant ID, DCE URI, DCR immutable ID, and DCR name (see [Retrieve the DCR name](#retrieve-the-dcr-name)).
- The selected resource group contains the DCR.
- The deploying account can create the Automation account and assign a role on the DCR.

### The runbook cannot authenticate to Azure Monitor

Verify that:

- The Automation account has a system-assigned managed identity.
- `UseManagedIdentity` is `true` in `GlobalConfiguration`.
- The managed identity has **Monitoring Metrics Publisher** on the DCR.
- The DCE URI and DCR immutable ID are correct.

### Microsoft Graph or Exchange Online access fails

Verify:

- `Group.Read.All`, `User.Read.All`, and `AuditLog.Read.All`.
- `Exchange.ManageAsApp`.
- The **Global Reader** or **Security Reader** directory role.

### Required modules are missing

Verify that the Automation account contains:

- `ExchangeOnlineManagement`
- `Microsoft.Graph.Authentication`
- `Microsoft.Graph.Users`
- `Microsoft.Graph.Groups`

### No data appears

1. Run `Start-ESICollector` manually.
2. Review the Automation job output and errors.
3. Confirm that `SentinelLogIngestionAPIActivated` and `UseManagedIdentity` are `true`.
4. Verify the DCE URI, DCR immutable ID, and stream name.
5. Run the validation query after several minutes.

## Related documentation

- [Exchange Security Insights Collector prerequisites and permissions](./ESICollector.md)
- [Collector configuration parameters](../Solutions/ESICollector/Parameters.md)
- [Collector upgrade instructions](../Solutions/ESICollector/README.md)
