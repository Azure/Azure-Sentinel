# Lock SAP User from Teams - Basic

< 🏡[home](../README.md)

Sophisticated scenario distinguishing between SAP maintenance events and malicious deactivation of the audit log ingestion into Sentinel using Azure Center for SAP Solutions health APIs.

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
| [Sentinel Responder](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#microsoft-sentinel-responder) | At least resource group where Sentinel lives | Required for Incident state update |
| [Azure Center for SAP solutions reader](https://learn.microsoft.com/azure/sap/center-sap-solutions/manage-with-azure-rbac) | Subscription level | Required for Azure resource graph SAP Virtual Instance discovery by Sentinel known SAP SID |
| [Virtual Machine Contributor](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#virtual-machine-contributor) | At least resource group/virtual machine where Sentinel Collector runs | Required for remediation option to restart the collector VM |

Learn more about Microsoft Sentinel built-in roles [here](https://learn.microsoft.com/azure/sentinel/roles) and Azure built-in roles [here](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles).

[🔝](#)
