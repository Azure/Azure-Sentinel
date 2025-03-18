# ESI Collector - Update

- [ESI Collector - Update](#esi-collector---update)
  - [Overview](#overview)
  - [Azure Automation Manual Update -- For Runbook Deployment](#azure-automation-manual-update----for-runbook-deployment)
    - [Runbook update](#runbook-update)
    - [Configuration update](#configuration-update)
  - [On-Premises Script Manual Update -- For On-Premises Deployment](#on-premises-script-manual-update----for-on-premises-deployment)
    - [Script update](#script-update)
    - [Script Configuration update](#script-configuration-update)
  - [Install ESI Collector Updater](#install-esi-collector-updater)

## Overview

The ESI Collector is a PowerShell script that collects security-related data from Exchange Online and sends it to a Log Analytics workspace. The script is designed to be run as a scheduled task and can be configured to collect data at different intervals.

## Azure Automation Manual Update -- For Runbook Deployment

### Runbook update

If you are using Azure Automation to run the ESI Collector, you can update the script by following these steps:

1. Download the latest version of the ESI Collector script from the [GitHub repository](https://aka.ms/ESI-ExchangeCollector-RawScript).
2. Open the Automation account in the Azure portal.
3. Navigate to the "Runbooks" section and select the ESI Collector runbook.
4. Click on "Edit" to open the runbook editor.
5. Replace the existing script with the new version of the ESI Collector.
6. Publish the Runbook to save the changes.
7. Test the updated script to ensure that it is working correctly.

### Configuration update

After updating the script, you may need to update the configuration settings if needed to add new features or fix issues. The configuration can be found in the GlobalConfiguration variable of your Automation Account.

The new version of the ESI Collector may introduce new configuration settings or change the existing ones. You can find the new configuration settings in GitHub repository or in the release notes : [GitHub repository](./../../ESICollector/README.md).

To update the configuration settings:

1. Open the Automation account in the Azure portal.
2. Navigate to the "Variables" section and select the GlobalConfiguration variable.
3. Update the configuration settings as needed.
4. Save the changes.
5. Test the updated script to ensure that it is working correctly.

## On-Premises Script Manual Update -- For On-Premises Deployment

### Script update

If you are running the ESI Collector as a scheduled script on a VM or server, you can update the script by following these steps:

1. Download the latest version of the ESI Collector script (CollectExchSecIns.zip) from the [GitHub repository](./../../ESICollector).
2. Replace the existing PS1 scripts with the new version of the ESI Collector found in the downloaded ZIP (CollectExchSecIns.ps1, setup.ps1, Updater.ps1).
3. Test the updated script to ensure that it is working correctly.

### Script Configuration update

After updating the script, you may need to update the configuration settings if needed to add new features or fix issues. The configuration can be found in the Config\CollectExchSecConfiguration.json file.

The new version of the ESI Collector may introduce new configuration settings or change the existing ones. You can find the new configuration settings in GitHub repository or in the release notes : [GitHub repository](./../../ESICollector).

To update the configuration settings:

1. Open the CollectExchSecConfiguration.json file.
3. Update the configuration settings as needed.
4. Save the changes.
5. Test the updated script to ensure that it is working correctly.

## Install ESI Collector Updater

**Under Construction**
