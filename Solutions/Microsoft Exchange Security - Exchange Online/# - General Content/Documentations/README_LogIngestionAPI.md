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
8. [Verify or assign **Monitoring Metrics Publisher** on the DCR](#verify-or-assign-monitoring-metrics-publisher-on-the-dcr).
9. If the managed identity was recreated, [assign the Microsoft Graph and Exchange Online permissions](#assign-microsoft-graph-and-exchange-online-permissions) and the [Microsoft Entra directory role](#assign-a-microsoft-entra-directory-role) again.
10. Run the runbook manually and verify ingestion before relying on the schedule.

## Update an existing Azure Automation deployment

> [!IMPORTANT]
> Do not use **Deploy to Azure** as the standard update method for an existing Automation account. The current template generates a new job schedule association identifier during each deployment and uses a fixed runbook content version. A redeployment has not been validated as an idempotent update path.

Update the existing Automation account manually:
1. Determine whether the existing `GlobalConfiguration` Automation variable is encrypted:
   - In the Automation account, open **Shared Resources** > **Variables** > **GlobalConfiguration**.
   - If the variable is not encrypted, copy its current value to a secure backup and modify only the properties listed in step 6.
   - If the variable is encrypted, retrieve and back up its complete decrypted value by using a temporary runbook:
     1. In the existing Automation account, open **Process Automation** > **Runbooks**.
     2. Select **Create a runbook**.
     3. Enter a temporary name such as `Export-ESIGlobalConfiguration`.
     4. Select **PowerShell** as the runbook type and **5.1** as the runtime version.
     5. Create the runbook and paste the following code:

        ```powershell
        $value = Get-AutomationVariable -Name 'GlobalConfiguration'
        Write-Output $value
        ```

     6. Save and publish the temporary runbook.
     7. Start the runbook once and wait until its job status is **Completed**.
     8. Open the completed job, select **Output**, and copy the complete `GlobalConfiguration` value.
     9. Paste the complete value into a text or JSON editor. Keep an unchanged copy as the rollback backup.
2. Open the `Start-ESICollector` runbook in the Automation account.
3. Replace the runbook content with the latest `CollectExchSecIns.ps1` content.
4. Save and publish the runbook.
5. Update `GlobalConfiguration` while preserving every unrelated setting:
   - **Non-encrypted variable:** Open **Shared Resources** > **Variables** > **GlobalConfiguration**, select **Edit**, and add or modify only the properties listed in step 6.
   - **Encrypted variable:** In the editor, add or modify only the properties listed in step 6 in the complete value retrieved from the temporary runbook. Validate that the result is complete, valid JSON. Then open **Shared Resources** > **Variables** > **GlobalConfiguration**, select **Edit**, replace the entire value with the updated content, and save it.
6. In the `LogCollection` section, set or update:
   - `SentinelLogIngestionAPIActivated` to `true`.
   - `DataCollectionEndpointURI` to the DCE URI displayed by the connector.
   - `DCRImmutableId` to the immutable ID displayed by the connector.
   - `UseManagedIdentity` to `true`.
   - `TargetLogTenantID` to the Microsoft Entra tenant ID.
   - `LogTypeName` to `ESIExchangeOnlineConfig`.
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
7. Verify that the required PowerShell 5.1 modules are installed.
8. [Verify or assign **Monitoring Metrics Publisher** on the DCR](#verify-or-assign-monitoring-metrics-publisher-on-the-dcr).
9. Verify that the existing daily schedule remains enabled and linked to `Start-ESICollector`.
10. If a temporary runbook was created, remove `Export-ESIGlobalConfiguration` and its completed job after the updated collector has been validated.

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

### Verify or assign Monitoring Metrics Publisher on the DCR

The system-assigned managed identity of the Automation account must have the **Monitoring Metrics Publisher** Azure role on the DCR used by the collector. Assign the role at the DCR scope to follow the principle of least privilege.

To create the role assignment, your account must have `Microsoft.Authorization/roleAssignments/write` at the DCR scope or a parent scope. For example, use **Role Based Access Control Administrator**, **User Access Administrator**, or **Owner**.

#### Verify the role in the Azure portal

1. Open the Automation account.
2. Go to **Account Settings** > **Identity** > **System assigned**.
3. Confirm that the status is **On**, then copy the **Object (principal) ID**.
4. Open the DCR identified in [Retrieve the DCR name](#retrieve-the-dcr-name).
5. Select **Access control (IAM)** > **Role assignments**.
6. Search for `Monitoring Metrics Publisher`.
7. Confirm that an assignment exists for the Automation account managed identity:
   - The role is **Monitoring Metrics Publisher**.
   - The member matches the Automation account name or the object ID copied in step 3.
   - The scope is the current DCR or a parent scope from which the role is inherited.

An inherited assignment is effective on the DCR. Do not add a duplicate assignment if the same identity already has the role from a parent scope.

#### Add the role in the Azure portal

If no effective assignment exists:

1. On the DCR, select **Access control (IAM)** > **Add** > **Add role assignment**.
2. On the **Role** tab, search for and select **Monitoring Metrics Publisher**, then select **Next**.
3. For **Assign access to**, select **Managed identity**.
4. Select **Select members**.
5. Select the subscription and the managed identity type for Azure Automation accounts.
6. Select the existing Automation account, then choose **Select**.
7. Select **Review + assign**, review the DCR scope and identity, and select **Review + assign** again.
8. Return to **Role assignments** and verify that the new assignment appears. Azure RBAC changes can take several minutes to propagate.

#### Verify or add the role with Azure PowerShell

Run the following commands from a PowerShell session with `Az.Accounts`, `Az.Automation`, `Az.Monitor`, and `Az.Resources` installed:

```powershell
Connect-AzAccount
Set-AzContext -SubscriptionId "<subscription-id>"

$automationResourceGroup = "<automation-account-resource-group>"
$automationAccountName = "<automation-account-name>"
$dcrResourceGroup = "<DCR-resource-group>"
$dcrName = "<DCR-resource-name>"

$automationAccount = Get-AzAutomationAccount `
    -ResourceGroupName $automationResourceGroup `
    -Name $automationAccountName `
    -ErrorAction Stop

$principalId = $automationAccount.Identity.PrincipalId
if (-not $principalId) {
    throw "The Automation account system-assigned managed identity is not enabled."
}

$dcr = Get-AzDataCollectionRule `
    -ResourceGroupName $dcrResourceGroup `
    -Name $dcrName `
    -ErrorAction Stop

$roleName = "Monitoring Metrics Publisher"
$roleAssignment = Get-AzRoleAssignment `
    -ObjectId $principalId `
    -RoleDefinitionName $roleName `
    -Scope $dcr.Id `
    -ErrorAction SilentlyContinue

if ($roleAssignment) {
    Write-Output "'$roleName' is already assigned to '$automationAccountName' on '$($dcr.Name)'."
}
else {
    New-AzRoleAssignment `
        -ObjectId $principalId `
        -RoleDefinitionName $roleName `
        -Scope $dcr.Id `
        -ErrorAction Stop

    Write-Output "'$roleName' was assigned to '$automationAccountName' on '$($dcr.Name)'."
}
```

This PowerShell check targets an assignment made directly on the DCR. Before creating it, use the portal procedure to confirm that the same role is not already inherited from a parent scope.

For general Azure RBAC procedures, see [Assign Azure roles using the Azure portal](https://learn.microsoft.com/azure/role-based-access-control/role-assignments-portal) and [Assign Azure roles using Azure PowerShell](https://learn.microsoft.com/azure/role-based-access-control/role-assignments-powershell).

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
