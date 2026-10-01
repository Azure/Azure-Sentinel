# Microsoft Exchange Security for Exchange On-Premises documentation

This folder contains the documentation for deploying and operating the **Microsoft Exchange Security for Exchange On-Premises** solution in Microsoft Sentinel.

The on-premises collector runs on a Windows server as a scheduled PowerShell task and uses certificate authentication to send data through the Azure Monitor Log Ingestion API.

## Collector deployment and configuration

- [Configure the Exchange Security Insights On-Premises Collector with Azure Monitor](./README_LogIngestionAPI.md): Deploy or upgrade the Azure Monitor data connector, configure certificate authentication, validate ingestion, and troubleshoot the deployment.

- [Exchange Security Insights Collector prerequisites and permissions](./ESICollector.md): Review the required PowerShell modules, Active Directory feature, Exchange permissions, and network access.

- [Configure the collector with WinformConfig](./WinformConfigReadme.md): Create or update `CollectExchSecConfiguration.json`, validate the settings, and create the mandatory Windows scheduled task.

## Forwarder

- [Forwarder quick start](../Forwarder/QUICKSTART-Forwarder.md): Configure pickup mode, test one file, and install the Forwarder scheduled task.

- [Forwarder Pickup Processor reference](../Forwarder/README-ForwarderPickup.md): Review authentication modes, configuration settings, script parameters, file handling, monitoring, and troubleshooting.

## Workbooks

- [Deploy the Microsoft Exchange Security workbooks](./WorkbookDeployement.md): Deploy and configure the workbooks used by the solution.

- [Delegate access to the workbooks](./WorkbookDelegation.md): Configure Microsoft Entra groups, custom roles, resource group permissions, and Log Analytics access for delegated workbook users.

## VIP monitoring

- [Configure VIP management](./VIPManagement.md): Configure the watchlist used to identify and monitor VIP activity in the Microsoft Exchange Security workbooks.
