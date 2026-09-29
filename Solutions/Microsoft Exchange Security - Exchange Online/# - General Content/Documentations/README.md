# Microsoft Exchange Security for Exchange Online documentation

This folder contains the documentation for deploying and operating the **Microsoft Exchange Security for Exchange Online** solution in Microsoft Sentinel.

The Exchange Online collector runs as a PowerShell runbook in Azure Automation and uses the Automation account's system-assigned managed identity.

## Collector deployment and configuration

- [Configure the Exchange Security Insights Online Collector with Azure Monitor](./README_LogIngestionAPI.md): Deploy or upgrade the Azure Monitor data connector and Azure Automation collector, configure the managed identity, validate ingestion, and troubleshoot the deployment.

- [Exchange Security Insights Collector prerequisites and permissions](./ESICollector.md): Review the required Azure Automation modules, Microsoft Graph permissions, Exchange Online permissions, Microsoft Entra directory role, and network access.

## Workbooks

- [Deploy the Microsoft Exchange Security workbooks](./WorkbookDeployement.md): Deploy and configure the workbooks used by the solution.

- [Delegate access to the workbooks](./WorkbookDelegation.md): Configure Microsoft Entra groups, custom roles, resource group permissions, and Log Analytics access for delegated workbook users.

## VIP monitoring

- [Configure VIP management](./VIPManagement.md): Configure the watchlist used to identify and monitor VIP activity in the Microsoft Exchange Security workbooks.
