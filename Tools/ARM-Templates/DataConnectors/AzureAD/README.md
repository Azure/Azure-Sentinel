# Azure Active Directory connector template

Author: Javier Soriano

This template enables the Azure AD connector on your Sentinel workspace. 

Azure Active Directory Audit/SignIn logs - requires permissions at tenant scope. Be aware that the User or SPN needs Owner rights on tenant scope for this operation, can be added with following CLI

`az role assignment create --role Owner --scope "/" --assignee {13ece749-d0a0-46cf-8000-b2552b520631}#>`

Required parameter is workspaceResourceId in format: 

`/subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}/providers/microsoft.operationalinsights/workspaces/{workspaceName}`

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fjaviersoriano%2FAzure-Sentinel%2Fjavier-arm%2FTools%2FARM-Templates%2FDataConnectors%2FAzureAD%2FAzureAD.json)