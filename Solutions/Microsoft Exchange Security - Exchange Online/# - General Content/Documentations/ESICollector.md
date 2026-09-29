# Exchange Security Insights Collector for Exchange Online

## Overview

The Exchange Security Insights Collector generates a snapshot of the Exchange Online configuration for the Microsoft Exchange Security for Exchange Online solution in Microsoft Sentinel. The Azure Automation runbook is scheduled to run at least once a day so that Microsoft Sentinel receives an up-to-date view of the environment.

The collector uses Exchange Online and Microsoft Graph PowerShell cmdlets to retrieve the information required to assess the security posture of the Exchange Online environment.

For a detailed description of the configuration settings, see the [configuration parameter reference](../Solutions/ESICollector/Parameters.md). For version-specific upgrade instructions, see the [Exchange Security Insights Collector README](../Solutions/ESICollector/README.md).

## Prerequisites

### Azure Automation PowerShell modules

In the Azure portal, open the Automation account and verify that the following modules are available for the PowerShell 5.1 runtime:

- `ExchangeOnlineManagement`
- `Microsoft.Graph.Authentication`
- `Microsoft.Graph.Users`
- `Microsoft.Graph.Groups`

Import or update missing modules from the Automation account's module gallery. When importing the Microsoft Graph modules, wait for `Microsoft.Graph.Authentication` to finish importing before importing `Microsoft.Graph.Users` and `Microsoft.Graph.Groups`.

If collector summary logs are stored in an Azure Storage account, the `Az.Storage` module must also be imported into the Automation account.

## Required permissions

The required Microsoft Graph and Exchange Online application permissions are not assigned automatically during deployment. Use the [`ExchangeOnlinePermSetup.ps1`](../Solutions/ESICollector/OnlineDeployment/ExchangeOnlinePermSetup.ps1) script to assign them to the managed identity of the Azure Automation account.

### Assign application permissions

Run the script from a workstation where the `Microsoft.Graph.Authentication` and `Microsoft.Graph.Applications` PowerShell modules are available. The account used to run the script must be a **Global Administrator** and must grant admin consent for the following delegated Microsoft Graph scopes requested by the script:

- `AppRoleAssignment.ReadWrite.All`
- `Application.Read.All`

Retrieve the object ID of the Automation account's managed identity from **Automation account** > **Account Settings** > **Identity**, and then run:

```powershell
.\ExchangeOnlinePermSetup.ps1 `
    -MIIDParam "<managed-identity-object-id>" `
    -TenantId "<tenant-id>" `
    -InteractiveAuth
```

The parameters are:

- `MIIDParam`: Object ID of the Automation account's managed identity. Use this parameter instead of modifying the `$MI_ID` placeholder in the script.
- `TenantId`: Optional tenant ID used for the Microsoft Graph connection.
- `InteractiveAuth`: Uses interactive authentication. Omit this switch to use device authentication.

The script assigns:

- `Group.Read.All`
- `User.Read.All`
- `AuditLog.Read.All`
- `Exchange.ManageAsApp`

The script creates app role assignments directly on the managed identity. It does not assign a Microsoft Entra directory role.

### Assign a Microsoft Entra role manually

Assign at least the **Global Reader** or **Security Reader** Microsoft Entra role to the managed identity so that the collector can read the Exchange Online configuration. For more information, see [Assign Microsoft Entra roles to the application](https://learn.microsoft.com/powershell/exchange/app-only-auth-powershell-v2?view=exchange-ps#assign-microsoft-entra-roles-to-the-application).

## Network access

The Azure Automation account must be able to reach:

- Microsoft Entra ID authentication endpoints
- Exchange Online
- Microsoft Graph
- `https://raw.githubusercontent.com`
- `https://*.ods.opinsights.azure.com`
- The configured Azure Monitor Data Collection Endpoint when the Log Ingestion API is enabled

## Collector summary logs in Azure Storage

When the UDS log destination is `AzureStorageAccount`:

- The `Az.Storage` PowerShell module must be available in the Automation account.
- The Automation account managed identity must have at least the **Storage Blob Data Contributor** role on the target storage account.
