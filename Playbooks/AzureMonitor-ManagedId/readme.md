# AzureMonitor-ManagedId

This playbook is an equivalent of AzureMonitor KQL query base block but allowing to use Managed Identity with HTTP request block.
Credits to @koosg for initial work.

## Prerequisite:

* Create Azure Integration account in same region than targeted logic app and load the liquid map as name 'azuremonitor'. (manual only at this point)
* Make role assignment "Log Analytics Reader" to managed identity for appropriate scope (target log analytics).

## Deploy to Azure
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAzureMonitor-ManagedId2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAzureMonitor-ManagedId%2Fazuredeploy.json)

## References

* https://medium.com/@koosg/secure-your-microsoft-sentinel-playbooks-with-managed-identities-fce1f232df3a
* https://www.m365princess.com/blogs/query-azure-monitor/
* https://learn.microsoft.com/en-us/azure/logic-apps/create-managed-service-identity?tabs=consumption
* https://learn.microsoft.com/en-us/rest/api/loganalytics/dataaccess/query/get?tabs=HTTP
* https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-enterprise-integration-liquid-transform?tabs=consumption
* https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-enterprise-integration-create-integration-account?tabs=azure-portal%2Cconsumption
