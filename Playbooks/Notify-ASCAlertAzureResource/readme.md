# Notify-ASCAlertAzureResource
author: Nathan Swift

This playbook will notify RBAC assigned Owners and Contributors both user and mail enabled security groups on the Azure Resource via a ASC alert generated Sentinel Incident.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FNotify-ASCAlertAzureResource%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FNotify-ASCAlertAzureResource%2Fazuredeploy.json)

**Additional Post Install Notes:**

The Logic App creates and uses a Managed System Identity (MSI) to authenticate and authorize against management.azure.com to obtain PrincipalIDs assigned to the Azure Resource. The MSI is also used to authenticate and authorize against graph.windows.net to obtains RBAC Objects by PrincipalIDs.

Assign RBAC 'Reader' role to the Logic App at the Subscription level.
Assign AAD Directory Role 'Directory readers' role to the Logic App.