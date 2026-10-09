# Update the Exchange Security Insights Collector

## Overview

The Exchange Security Insights Collector supports two execution models:

- Exchange Online runs as the `Start-ESICollector` runbook in Azure Automation.
- Exchange On-Premises runs as `CollectExchSecIns.ps1`, normally through a Windows scheduled task.

Review the [collector package and upgrade guide](../README.md) before updating. It identifies the current version, required configuration changes, and supported migration path.

## Before updating

1. Record the currently deployed collector version.
2. Review the version-specific changes in the [package and upgrade guide](../README.md).
3. Back up the current configuration:
   - Exchange Online: export the `GlobalConfiguration` Automation variable.
   - Exchange On-Premises: copy `Config\CollectExchSecConfiguration.json` to a secure backup location.
4. Preserve custom instance, add-on, scheduling, proxy, and storage settings.
5. If migrating to the Azure Monitor Log Ingestion API, deploy the updated Microsoft Sentinel solution and connector resources before enabling the new ingestion settings.

For setting definitions, see the [configuration parameter reference](../Parameters.md).

## Update an Exchange Online runbook

1. Download the latest [`CollectExchSecIns.ps1`](./CollectExchSecIns.ps1).
2. In the Azure portal, open the Automation account.
3. Open **Runbooks** and select `Start-ESICollector`.
4. Select **Edit**, replace the runbook content with the latest script, and save it.
5. Publish the runbook.
6. Update `GlobalConfiguration` only after comparing it with the new parameter reference. Preserve unrelated settings.
7. Verify that the required PowerShell modules, managed identity permissions, Microsoft Graph permissions, Exchange Online permissions, and Microsoft Entra directory role are still configured.
8. Run `Start-ESICollector` manually and confirm that the job completes successfully.
9. Verify that new data reaches the expected Log Analytics table before relying on the schedule.

For a complete Azure Monitor deployment or migration, follow the [solution-specific Azure Monitor guide](../../../Documentations/README_LogIngestionAPI.md).

## Update an Exchange On-Premises deployment

1. Download and unblock the latest `CollectExchSecIns.zip` package from the [collector package folder](../).
2. Extract the package to a new directory.
3. Follow the replacement procedure in the [collector package and upgrade guide](../README.md).
4. Preserve the backed-up `Config\CollectExchSecConfiguration.json` file unless the upgrade guide requires a schema change.
5. Apply the required configuration changes with [`setup.ps1`](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20On-Premises/%23%20-%20General%20Content/Documentations/ReadmeSetup.PS1.md). For an existing deployment, select configuration-only update mode.
6. Verify that the scheduled task points to the updated collector path.
7. Run the collector manually and confirm that it completes successfully.
8. Verify that new data reaches the expected Log Analytics table before relying on the scheduled task.

For a complete Azure Monitor deployment or migration, follow the [solution-specific Azure Monitor guide](../../../Documentations/README_LogIngestionAPI.md).

## Validate the update

After either update:

1. Confirm that the collector reports the expected version.
2. Review the collector or Automation job logs for authentication, permission, configuration, and ingestion errors.
3. Confirm that the most recent collection appears in Microsoft Sentinel.
4. Confirm that the scheduled task or Automation schedule is enabled.
5. Retain the backup until several scheduled executions have completed successfully.

If validation fails, stop the schedule, restore the backed-up configuration and previous collector version, and investigate the error before retrying the update.
