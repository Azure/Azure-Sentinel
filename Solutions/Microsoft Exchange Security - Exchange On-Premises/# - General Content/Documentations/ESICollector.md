# Exchange Security Insights Collector prerequisites and connectivity

This guide describes the server prerequisites, permissions, and network access required to run the Exchange Security Insights Collector in an on-premises Exchange environment.

For deployment and Azure Monitor configuration, see [Configure the Exchange Security Insights On-Premises Collector with Azure Monitor](./README_LogIngestionAPI.md). For package installation and upgrades, see the [collector package and upgrade guide](../Solutions/ESICollector/README.md). For individual settings, see the [configuration parameter reference](../Solutions/ESICollector/Parameters.md).

## Prerequisites

### Azure PowerShell module

> [!IMPORTANT]
> Version 8.0.0.0 requires the Azure PowerShell `Az.Accounts` module. Install or update this module on every Windows machine that runs the collector before upgrading.

Run the following commands in an elevated Windows PowerShell session to verify that the module and the `Connect-AzAccount` command are available:

```powershell
Get-Module -ListAvailable -Name Az.Accounts
Get-Command -Name Connect-AzAccount -Module Az.Accounts
```

If the module is not installed, install it from the PowerShell Gallery:

```powershell
Install-Module -Name Az.Accounts -Repository PSGallery -Scope AllUsers -Force
```

### Active Directory module for Windows PowerShell

> [!IMPORTANT]
> Before running the collector, verify that the Windows Server feature **Active Directory module for Windows PowerShell** is installed on the machine that runs the collector.

In Server Manager, this feature is located under **Add Roles and Features** > **Features** > **Remote Server Administration Tools** > **Role Administration Tools** > **AD DS and AD LDS Tools** > **Active Directory module for Windows PowerShell**.

You can verify the feature state from an elevated Windows PowerShell session:

```powershell
Get-WindowsFeature -Name RSAT-AD-PowerShell
```

The `Install State` must be `Installed`. If the feature is not installed, run:

```powershell
Install-WindowsFeature -Name RSAT-AD-PowerShell
```

After installation, verify that the `ActiveDirectory` module and its cmdlets are available:

```powershell
Import-Module ActiveDirectory
Get-Command -Name Get-ADDomain -Module ActiveDirectory
```

## Required permissions

The account that runs the collector must be a member of the **Organization Management** role group.

The collector must also be able to:

- Read Active Directory groups and their members, especially administrative groups in the **Microsoft Exchange Security Groups** organizational unit.
- Connect to every Exchange Server by using WMI and remote PowerShell.
- Contact the domain controllers by using the Active Directory PowerShell module.

Membership in **Organization Management** normally provides the required permissions. Additional configuration might be required if Active Directory inheritance has been disabled or unsupported custom hardening has been applied.

## Network access

### Internet access

The machine that runs the collector requires direct or proxy access to:

- `https://*.ods.opinsights.azure.com`
- `https://raw.githubusercontent.com`
- The configured Azure Monitor Data Collection Endpoint when the Log Ingestion API is enabled
- The Microsoft Entra and Azure endpoints used by `Connect-AzAccount`

Configure the proxy in `.\Config\CollectExchSecConfiguration.json`. Proxies that require explicit authentication are not supported.

### Exchange Server access

The collector must be able to connect to every Exchange Server by using remote PowerShell and WMI.

### Active Directory access

The collector must be able to connect to the domain controllers by using the Active Directory PowerShell module.
