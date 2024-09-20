# Remediate SAP Sentinel Collector Agent attack

< 🏡[home](../README.md)

Sophisticated scenario distinguishing between SAP maintenance events and malicious deactivation of the audit log ingestion into Sentinel.

Used Sentinel alert rule `[SAP - Data collection health check](https://learn.microsoft.com/azure/sentinel/monitor-sap-system-health#use-an-alert-rule-template)`

[Azure Center for SAP Solutions (ACSS)](https://learn.microsoft.com/azure/sap/center-sap-solutions/overview) health info exposed via the [Azure Resource Graph](https://learn.microsoft.com/azure/governance/resource-graph/overview) qualify the incident to drive better triage processes at the SAP Security Operations teams.

👨🏽‍🔧[**installation guide**](../INSTALLATION.md).

| Step | 🪂 |
| --- | --- |
| Logic Apps Infrastructure | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSAP%2FPlaybooks%2FSAPCollectorRemediate-STD%2Fazuredeploy.json) |
| Logic Apps Connections | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSAP%2FPlaybooks%2FSAPCollectorRemediate-STD%2Fazureconnectordeploy.json) |
| Logic Apps Standard Connections configuration | 🔗[link](connections.json) |
| Logic Apps Standard workflow | 🔗[link](workflow.json) |
| Logic Apps Standard workflow parameters | 🔗[link](workflowparameters.json) |

## Required Azure Roles

| Role Name | Resource Type Scope | Purpose |
| --- | --- | --- |
| [Microsoft Sentinel Responder](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#microsoft-sentinel-responder) | At least resource group where Sentinel lives | Required for Incident state update |
| [Azure Center for SAP solutions reader](https://learn.microsoft.com/azure/sap/center-sap-solutions/manage-with-azure-rbac) | Subscription level | Required for Azure resource graph SAP Virtual Instance discovery by Sentinel known SAP SID |
| [Virtual Machine Contributor](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#virtual-machine-contributor) | At least resource group/virtual machine where Sentinel Collector runs | Required for remediation option to restart the collector VM |

Learn more about Microsoft Sentinel built-in roles [here](https://learn.microsoft.com/azure/sentinel/roles) and Azure built-in roles [here](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles).

## Additional integration options with Azure Resource Graph query for ACSS

[Azure Resource Graph Explorer🔗](https://portal.azure.com/?#view/HubsExtension/ArgQueryBlade)

This playbook uses below query (dynmic SID param coming from Sentinel). Get inspired from it to expand to your own scenarios.

Find the REST API docs for the resource graph [here](https://learn.microsoft.com/rest/api/azureresourcegraph/resourcegraph(2021-03-01)/resources/resources?tabs=HTTP).

`POST https://management.azure.com/providers/Microsoft.ResourceGraph/resources?api-version=2021-03-01`

BODY

```sql
// Global SAP ACSS details by SID
// Click the "Run query" command above to execute the query and see results.
resources
| where type =~ 'Microsoft.Workloads/sapVirtualInstances' //get all resources of type SAP Virtual Instance
| where name == 'P01' //get selected SAP SID
| project id,name,tenantId,resourceGroup,subscriptionId,properties.health,properties.status //get only required fields
```

[🔝](#)
