# Configure the Exchange Security Insights Collector with WinformConfig

## Overview

WinformConfig is the graphical configuration editor included with the Exchange Security Insights Collector. Use it to create or update `Config\CollectExchSecConfiguration.json`, validate the configuration, review changes, and create the collector's scheduled task.

The editor is started by:

```text
WinformConfig\SetupCollectExchSecConfiguration.ps1
```

> [!NOTE]
> The PowerShell entry point is `SetupCollectExchSecConfiguration.ps1`.

For Azure Monitor ingestion, deploy the **Exchange Security Insights On-Premises Collector (Azure Monitor)** data connector before using the editor. The connector creates the Azure resources, application, and permissions. WinformConfig is then used to apply the connector values to the local collector configuration.

## Requirements

Before starting the editor, verify that:

- The complete `WinformConfig` folder from the collector package is present.
- `Config\CollectExchSecConfiguration.json` exists or you have selected a location for a new configuration.
- Windows PowerShell 5.1 is available.
- You are running an elevated Windows PowerShell session.
- You are a local administrator so that the mandatory scheduled task can be created.
- The downloaded ZIP file or all files under the extracted `WinformConfig` folder have been unblocked.
- The service account used by the scheduled task has the permissions documented in [Exchange Security Insights Collector for Exchange Server](./ESICollector.md).
- An authentication certificate has been created and installed with its private key in a certificate store accessible to the service account.
- The public part of the certificate has been added to the Entra application used by the collector.

Back up an existing configuration before modifying it.

## Choose your scenario

### New deployment

For a new deployment:

1. Start with the configuration file included in the latest collector package.
2. Complete the full WinformConfig workflow described below.
3. Create the mandatory scheduled task during the same configuration session.
4. Save the configuration.
5. Run the collector manually and verify ingestion before relying on the task.

### Existing deployment

When updating an existing deployment:

1. Back up `Config\CollectExchSecConfiguration.json`.
2. Open the existing file by using the `ConfigPath` parameter.
3. Update only the Azure Monitor ingestion and certificate settings, preserving all environment, instance, add-on, and other custom settings.
4. Verify that the mandatory scheduled task points to the updated collector. If it is missing, create it during the same configuration session.
5. Optionally, use **Diff Summary** to review the changes.
6. Save the existing file.
7. Run the collector manually and verify ingestion.

Both scenarios continue with the editor startup and configuration workflow below.

> [!IMPORTANT]
> Before starting the editor, unblock the downloaded collector package or the extracted WinformConfig files as described in the [collector update instructions](../Solutions/ESICollector/README.md#collector-update).

## Start the editor

Open an elevated Windows PowerShell session in the collector directory and run:

```powershell
.\WinformConfig\SetupCollectExchSecConfiguration.ps1
```


## Read-only and write modes

The editor starts in **Read-Only** mode. In this mode, you can inspect the configuration, but controls that modify or save data are disabled.

Select **Mode: Read-Only** on the left side of the status bar to switch to **Mode: Write** before making changes. The button changes from light gray to light green when write mode is enabled.

Switching modes does not save the configuration automatically.

## Recommended configuration workflow

### 1. Deploy the Microsoft Sentinel data connector

Before opening WinformConfig, configure **Exchange Security Insights On-Premises Collector (Azure Monitor)** in Microsoft Sentinel and select **Deploy Exchange Collector Push connector resources**.

The connector page provides:

- Tenant ID.
- Entra application ID.
- Data Collection Endpoint URI.
- DCR immutable ID.
- Stream name.

Use these values when completing the editor. Do not create another DCR or Entra application from WinformConfig when the connector has already created them.

### 2. Prepare the authentication certificate

The on-premises collector uses certificate authentication and does not use an application secret.

Create and install the certificate by following [Create the authentication certificate](./README_LogIngestionAPI.md#create-the-authentication-certificate).

Before continuing in WinformConfig, verify that:

1. The certificate and its private key are installed in `Cert:\LocalMachine\My`.
2. The collector's service account can read the private key.
3. The public certificate has been added to the Entra application created by the data connector.
4. The certificate thumbprint is available for the collector configuration.

### 3. Configure the basic information

In the setup view, select:

- **Target:** `On-Premises`
- **Execution environment:** (Where will the script run ?) `Server`
- **Identification Environment** : Enter the name of your environment that will be displayed in the workbook
- **Instance type:** Select `Def` for the standard Exchange configuration assessment. The `IoC` option is currently in beta and is intended only for the IIS IoC scenario.
- **Ingestion API:** `AzureMonitorAPI`

Set the environment identification value used by the Microsoft Sentinel workbooks. The default `#ForestName#` value is replaced with the forest name for an on-premises deployment.

### 4. Configure Azure Monitor API information

Select **Azure MonitorAPI Information** and enter the values displayed on the data connector page.

The editor updates the corresponding collector settings, including:

- `LogCollection.SentinelLogIngestionAPIActivated`
- `LogCollection.TargetLogTenantID`
- `LogCollection.TargetLogAppID`
- `LogCollection.TargetLogCertificateThumbprint`
- `LogCollection.DataCollectionEndpointURI`
- `LogCollection.DCRImmutableId`

Enter the thumbprint of the certificate prepared in the previous step.

### 5. Configure Exchange Server

Select **Exchange On-Premises information**.

Verify the Exchange Server binary path. The default is:

```text
C:\Program Files\Microsoft\Exchange Server\V15\bin
```

Enter the Exchange version.

> [!NOTE]
> Ignore **Instance Information** for the standard deployment.

### 6. Configure and create the scheduled task

The scheduled task should be configured during the same WinformConfig setup session as the other collector parameters.

In the **Server Execution** section, provide:

- A unique scheduled-task name.
- The daily start time in `hh:mmAM` or `hh:mmPM` format, for example `11:00PM`.
- The service account in UPN format, for example `svc-exchange@contoso.com`.
  - This account must be a member of the **Organization Management** role group.
- The service account password.

Select **Create the Schedule Task** after reviewing the values.

The editor creates a Windows scheduled task that:

- Runs `CollectExchSecIns.ps1` with Windows PowerShell.
- Runs once a day at the selected time.
- Ignores a new invocation when a previous execution is still running.
- Retries a failed execution up to five times at one-hour intervals.
- Has a maximum execution time of 23 hours.

If a task with the same name already exists, verify that it points to the current collector. Reuse the existing task during an upgrade instead of creating a duplicate.

### 7. Review and save

Before saving:

1. Optionally, open **Tools** > **Diff Summary** to review the proposed changes.
2. Confirm that all required fields are populated.
3. Select **File** > **Save** to update the current file, or **Save As** to create another configuration file.

The editor validates mandatory fields before saving. **Save As** can allow a configuration with missing mandatory values after displaying a warning; such a configuration might fail when the collector runs.

## Other editor capabilities

WinformConfig also provides:

- **Advanced Configuration** for settings outside the initial setup workflow.
- **Configuration Metadata** for configuration version information.
- **Raw Editor** for viewing or editing the complete JSON.
- **Paste JSON** and **Copy JSON** clipboard operations.
- **Undo** and **Redo** with up to 30 snapshots.
- Per-field restore and conditional field visibility.
- Editors for arrays, add-ons, UDS log processors, and instance configurations.
- **Open**, **Save**, and **Save As** operations.

Use the raw and advanced editors only when the standard setup workflow does not expose the required setting.

## Logs

WinformConfig writes logs under:

```text
WinformConfig\Helpers\logs
```

The files include:

- `actions_*.log`: user actions and editor events.
- `telemetry_*.jsonl`: structured session events.
- `errors_*.log`: detailed error information.

Files older than `LogRetentionDays` are removed when the editor starts.

## Troubleshooting

### Save controls are disabled

The editor is in read-only mode. Select **Mode: Read-Only** on the left side of the status bar to switch to write mode.

### A section or field is not displayed

Fields are displayed conditionally. Verify the target, execution environment, instance type, ingestion API, and authentication selections in the basic setup sections.

### The configuration file is not loaded

Provide the full configuration path:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
    -File .\WinformConfig\SetupCollectExchSecConfiguration.ps1 `
    -ConfigPath "C:\Path\To\Config\CollectExchSecConfiguration.json"
```

### Scheduled-task creation fails

Verify that:

- Windows PowerShell is running as administrator.
- The start time uses the required AM/PM format.
- The service account is in UPN format.
- The password is correct.
- The task name is not already in use.
- The service account has the required Exchange and Active Directory permissions.

### The editor reports an unexpected error

Review the latest `errors_*.log` and `actions_*.log` files under `WinformConfig\Helpers\logs`.

## Related documentation

- [Configure Azure Monitor ingestion](./README_LogIngestionAPI.md)
- [Exchange Security Insights Collector prerequisites](./ESICollector.md)
- [Collector configuration parameters](../Solutions/ESICollector/Parameters.md)
- [Collector upgrade instructions](../Solutions/ESICollector/README.md)
