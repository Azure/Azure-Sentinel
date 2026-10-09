# Configure the Exchange Security Insights Collector with setup.ps1

## Overview

`setup.ps1` is the interactive command-line configuration script included in the root of the Exchange Security Insights Collector package. It:

1. Loads an existing `CollectExchSecConfiguration.json` file.
2. Configures Azure Monitor Log Ingestion API or legacy Log Analytics API settings.
3. Optionally stops after updating only the ingestion settings in the JSON file.
4. In full setup mode, configures the collector environment and processing type.
5. Creates a timestamped backup of the existing JSON configuration.
6. Saves the updated JSON configuration.
7. In full setup mode, creates the mandatory daily Windows scheduled task.

The script updates an existing configuration file; it does not create a complete configuration from an empty file.

> [!IMPORTANT]
> The configuration file is saved before the scheduled task is created. If task creation fails, the JSON changes remain in place.

## Requirements

Before running `setup.ps1`, verify that:

- The complete collector package has been downloaded and extracted.
- Windows PowerShell 5.1 is available.
- You are a local administrator and can open an elevated Windows PowerShell session.
- `CollectExchSecIns.ps1`, `setup.ps1`, and `Config\CollectExchSecConfiguration.json` are present in the collector directory.
- The collector directory path does not contain spaces. The scheduled-task action created by the current script does not add quotation marks around the collector script path.
- The account that will run the scheduled task:
  - Uses a UPN, for example `svc-exchange@contoso.com`.
  - Is a member of the Exchange **Organization Management** role group.
  - Can access the Exchange servers through remote PowerShell and WMI.
  - Can query Active Directory.
- The server meets the module and network requirements in [Exchange Security Insights Collector prerequisites and permissions](./ESICollector.md).

The script creates an automatic backup before overwriting the configuration. An additional backup outside the collector directory is still recommended before a collector upgrade.

## Prepare the ingestion information

### Azure Monitor Log Ingestion API

For the recommended Azure Monitor Log Ingestion API, have the following values ready:

- Data Collection Endpoint (DCE) URI.
- Data Collection Rule (DCR) immutable ID.
- Authentication information for one of these modes:
  - A system-assigned managed identity with the **Monitoring Metrics Publisher** role on the DCR.
  - A Microsoft Entra tenant ID, application (client) ID, and certificate thumbprint.

The Microsoft Sentinel data connector displays the DCE URI and DCR immutable ID after its resources are deployed. See [Configure the Exchange Security Insights On-Premises Collector with Azure Monitor](./README_LogIngestionAPI.md) for connector deployment and certificate preparation.

> [!IMPORTANT]
> The script proposes certificate authentication as the default choice. Select managed identity only when the collector host has a usable system-assigned managed identity, such as an appropriately configured Azure VM. For a physical server or a VM without an Azure managed identity, answer `N`, or press **Enter**, to use certificate authentication.

When certificate authentication is used:

- The certificate and its private key must be installed in a certificate store accessible to the scheduled-task account.
- The public certificate must be uploaded to the Microsoft Entra application.
- The scheduled-task account must have read access to the certificate private key.
- The application identity must have the **Monitoring Metrics Publisher** role on the DCR.

### Legacy Log Analytics API

The legacy mode requires:

- Log Analytics workspace ID.
- Log Analytics workspace key.

The workspace key is stored in clear text in the JSON configuration. Restrict access to the configuration file and use the Azure Monitor Log Ingestion API for new deployments.

## Script parameters

All parameters are optional.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `JSONFileCondiguration` | `.\Config\CollectExchSecConfiguration.json` | Existing JSON file to update. The spelling `Condiguration` is part of the script parameter name and must be used exactly as shown. |
| `Instance` | `Default` | Collector instance passed to `CollectExchSecIns.ps1` by the scheduled task. For IIS IoC processing, the script forces this value to `IIS-IoCs`. |
| `AdditionalName` | Empty | Optional suffix added to the Windows scheduled-task name. It does not change the collector instance or the JSON configuration. |

> [!WARNING]
> `JSONFileCondiguration` controls which file `setup.ps1` updates, but the generated scheduled task does not pass this path to `CollectExchSecIns.ps1`. The task therefore uses `.\Config\CollectExchSecConfiguration.json`. Keep the active configuration at this default location, or manually correct the scheduled-task action after setup.

For a non-default instance, the corresponding entry must already exist under `InstanceConfiguration` in the JSON file. The setup script does not create custom instance definitions.

## Start the script and create the automatic backup

Open **Windows PowerShell 5.1 as Administrator** and change to the collector directory:

```powershell
Set-Location -LiteralPath 'C:\CollectExchSecIns'
```

Immediately before overwriting the JSON file, the script creates a backup in the same directory. Its name uses the original file name followed by a `yy-MM-dd-HHmm` timestamp:

```text
CollectExchSecConfiguration-26-09-25-1500.json
```

Windows file names cannot contain `:`, so the hour and minute are written as `1500` instead of `15:00`.

If a backup with the same timestamp already exists, the script adds a numeric suffix such as `-1`. If the backup cannot be created, setup stops and does not overwrite the original configuration.

If the downloaded script is blocked, unblock it:

```powershell
Unblock-File -LiteralPath '.\setup.ps1'
```

Run setup with the default configuration and instance:

```powershell
.\setup.ps1
```

To configure an existing named instance:

```powershell
.\setup.ps1 -Instance 'Contoso' -AdditionalName 'Production'
```

To explicitly identify the configuration file:

```powershell
.\setup.ps1 -JSONFileCondiguration '.\Config\CollectExchSecConfiguration.json'
```

Run the script from the collector directory. The default configuration path is relative to the current PowerShell directory, not to the location of `setup.ps1`.

## Complete the interactive setup

### 1. Choose the setup scope

At the first prompt, choose whether setup should only update the ingestion settings in `CollectExchSecConfiguration.json`:

```text
Do you only want to update CollectExchSecConfiguration.json (for example, to switch to Azure Monitor Log Ingestion API)? (Y/N, default N)
```

- Enter `Y` to switch the configuration to the Azure Monitor Log Ingestion API and update its authentication settings. Azure Monitor is selected automatically; the script does not ask for `AM` or `LA`. After the values are collected, it creates the automatic backup, saves the JSON file, and exits.
- Enter `N`, or press **Enter**, to run the complete setup.

Configuration-only mode always sets:

- `LogCollection.SentinelLogIngestionAPIActivated` to `true`.
- `LogCollection.TogetherMode` to `false`.
- `LogCollection.ExportDomainsInformation` to the JSON Boolean `true`. The obsolete `Global.ExportDomainsInformation` property is removed when present.
- `Advanced.MaximalSentinelPacketSizeMb` to the JSON number `0.9`.

Every Azure Monitor property written by configuration-only mode is created when it does not already exist in the corresponding JSON section.

In configuration-only mode, the script does not request or change:

- Environment identification.
- Analysis type.
- On-premises or Exchange Online target.
- Exchange binary path.
- Scheduled-task time, account, or password.

It does not create or modify a Windows scheduled task.

### 2. Select the ingestion API

This selection is displayed only during full setup. Configuration-only mode selects Azure Monitor automatically.

At the following prompt, enter:

- `AM` for the Azure Monitor Log Ingestion API. Pressing **Enter** also selects `AM`.
- `LA` for the legacy Log Analytics API. This option is deprecated and should not be used.

```text
Which ingestion API do you want to use? Azure Monitor Log Ingestion API (AM, default) or legacy Log Analytics API (LA)
```

#### Azure Monitor selection

When `AM` is selected, enter:

1. The complete DCE URI, for example `https://<dce-name>.<region>-1.ingest.monitor.azure.com`.
2. The DCR immutable ID, normally beginning with `dcr-`.
3. Whether to use managed identity:
   - Enter `Y` only when the host has a configured system-assigned managed identity.
   - Enter `N`, or press **Enter**, to use a certificate-based Microsoft Entra application.
4. If certificate authentication is selected, enter:
   - Microsoft Entra tenant ID.
   - Application (client) ID.
   - Certificate thumbprint.

The script sets:

- `LogCollection.SentinelLogIngestionAPIActivated` to `true`.
- `LogCollection.ExportDomainsInformation` to `true`, creating the property when necessary and removing its obsolete location under `Global`.
- `Advanced.MaximalSentinelPacketSizeMb` to `0.9`, creating the property when necessary.
- `LogCollection.DataCollectionEndpointURI`.
- `LogCollection.DCRImmutableId`.
- `LogCollection.UseManagedIdentity`.
- The tenant, application, and certificate fields when managed identity is not used.

The script does not enable `LogCollection.ActivateLogUpdloadToSentinel`. Verify separately that this existing setting is `true`.

#### Legacy Log Analytics selection

When `LA` is selected, enter:

1. Log Analytics workspace ID.
2. Log Analytics workspace key.

The script sets:

- `LogCollection.SentinelLogIngestionAPIActivated` to `false`.
- `LogCollection.UseManagedIdentity` to `false`.
- `LogCollection.WorkspaceId`.
- `LogCollection.WorkspaceKey`.

Existing Azure Monitor values are not removed, but they are ignored while `SentinelLogIngestionAPIActivated` is `false`.

### 3. Identify the environment

Enter the environment name that should appear in Microsoft Sentinel workbooks.

You can leave the value empty to let the collector use the forest name for an on-premises environment.

### 4. Select the analysis type

Enter one of the following values:

- `Def`: standard Exchange configuration assessment. This is the default when you press **Enter**, and the script displays a confirmation message.
- `IoC`: IIS indicator-of-compromise assessment.

For `IoC`, the script:

- Forces the instance name to `IIS-IoCs`.
- Sets `Global.ESIProcessingType` to `On-Premises`.

Only one IIS IoC scheduled instance should be configured.

### 5. Select the Exchange target

For the standard `Def` analysis, select:

- `OP`: Exchange Server on-premises. This is the default when you press **Enter**, and the script displays a confirmation message.
- `OL`: Exchange Online.

The script updates `Global.ESIProcessingType` to `On-Premises` or `Online`.

For `OP`, enter the Exchange binary path or press **Enter** to preserve the value already present in the JSON file. The standard path is:

```text
C:\Program Files\Microsoft\Exchange Server\V15\bin
```

After this step, the script saves the JSON configuration.

### 6. Configure the daily scheduled task

Provide:

1. A daily execution time in 12-hour format with `AM` or `PM`, for example `11:00PM`.
2. The service account in UPN format, for example `svc-exchange@contoso.com`.
3. The service account password.

The script creates a task named:

```text
ESI - Exchange Security Configuration Collector - <Instance>
```

When `AdditionalName` is provided, it is appended:

```text
ESI - Exchange Security Configuration Collector - <Instance> - <AdditionalName>
```

The scheduled task:

- Starts `CollectExchSecIns.ps1` with `powershell.exe`.
- Adds `-InstanceName '<Instance>'` for a non-default instance.
- Runs once a day at the selected time.
- Has a maximum execution time of 23 hours.
- Ignores a new start when a previous execution is still running.
- Retries a failed execution up to five times at one-hour intervals.

Before running setup again for the same instance, check whether a task with the same name already exists. The script does not use `-Force` when registering the task.

## Validate the configuration

### Validate the JSON file

Parse the saved file and display the non-secret settings:

```powershell
$config = Get-Content -LiteralPath '.\Config\CollectExchSecConfiguration.json' -Raw |
    ConvertFrom-Json

$config.Global |
    Select-Object EnvironmentIdentification, ESIProcessingType

$config.Advanced |
    Select-Object ExchangeServerBinPath, MaximalSentinelPacketSizeMb

$config.LogCollection |
    Select-Object ActivateLogUpdloadToSentinel,
        SentinelLogIngestionAPIActivated,
        TogetherMode,
        DataCollectionEndpointURI,
        DCRImmutableId,
        UseManagedIdentity,
        TargetLogTenantID,
        TargetLogAppID,
        TargetLogCertificateThumbprint,
        WorkspaceId
```

Do not display or copy `WorkspaceKey` into logs, tickets, or terminal transcripts.

### Validate the scheduled task

Replace the task name if a different instance or additional name was used:

```powershell
$taskName = 'ESI - Exchange Security Configuration Collector - Default'
$task = Get-ScheduledTask -TaskName $taskName

$task | Select-Object TaskName, State
$task.Actions | Select-Object Execute, Arguments
Get-ScheduledTaskInfo -TaskName $taskName |
    Select-Object LastRunTime, LastTaskResult, NextRunTime
```

Confirm that the action points to the intended collector directory and instance.

### Run the collector manually

Test the default instance:

```powershell
.\CollectExchSecIns.ps1
```

For a named instance, use the same name configured in the task:

```powershell
.\CollectExchSecIns.ps1 -InstanceName 'Branch01'
```

Review the collector output and logs, then validate ingestion by following [Validate data ingestion](./README_LogIngestionAPI.md#validate-data-ingestion).

## Troubleshooting

### The configuration file cannot be found

Run the script from the collector directory or pass the exact existing file path with `-JSONFileCondiguration`.

Remember that a custom path is not automatically added to the scheduled-task action.

### The JSON file cannot be parsed

Restore the backup, confirm that the file contains valid JSON, and run setup again. `setup.ps1` must load the file successfully before it can update it.

### The scheduled task cannot be registered

Verify that:

- Windows PowerShell is running as Administrator.
- The service account is entered in UPN format.
- The password is correct.
- The execution time is a valid 12-hour value such as `09:30PM`.
- A task with the same name does not already exist.

The JSON configuration has already been saved even when task registration fails.

### The task starts the wrong configuration

The generated task does not include the `-JSONFileCondiguration` collector parameter. Place the active configuration at `.\Config\CollectExchSecConfiguration.json` or update the task action to pass the intended file explicitly.

### Azure Monitor authentication fails

For certificate authentication, verify:

- Tenant ID and application ID.
- Certificate thumbprint without hidden characters.
- Certificate validity.
- Presence of the private key.
- Private-key read access for the scheduled-task account.
- Public certificate registration on the Microsoft Entra application.
- **Monitoring Metrics Publisher** assignment on the DCR.

For managed identity, verify:

- The collector host has a system-assigned managed identity.
- The identity has the **Monitoring Metrics Publisher** role on the DCR.
- The scheduled execution environment can request an Azure managed identity token.

### The task succeeds but no data is ingested

Verify that:

- `LogCollection.ActivateLogUpdloadToSentinel` is `true`.
- The selected ingestion API matches the configured values.
- The DCE URI and DCR immutable ID match the data connector.
- `LogCollection.LogTypeName` remains `ESIExchangeConfig`.
- The collector completes successfully when run manually.

## Related documentation

- [Configure the Exchange Security Insights On-Premises Collector with Azure Monitor](./README_LogIngestionAPI.md)
- [Exchange Security Insights Collector prerequisites and permissions](./ESICollector.md)
- [Collector configuration parameter reference](../Solutions/ESICollector/Parameters.md)
- [Collector package and upgrade guide](../Solutions/ESICollector/README.md)
