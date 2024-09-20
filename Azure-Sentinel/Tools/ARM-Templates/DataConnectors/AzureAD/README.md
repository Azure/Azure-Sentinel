# Azure Active Directory connector template

Author: Javier Soriano

This template enables the Azure AD connector on your Sentinel workspace. 

Azure Active Directory Audit/SignIn logs requires permissions to deploy at tenant scope. Assign Owner or Contributor to the principal that needs to deploy the templates (details [here](https://docs.microsoft.com/azure/azure-resource-manager/templates/deploy-to-tenant?tabs=azure-cli#required-access)):

`az role assignment create --role Owner --scope "/" --assignee {user object ID}`

Required template parameter is workspaceResourceId in format: 

`/subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}/providers/microsoft.operationalinsights/workspaces/{workspaceName}`

Try it with the link below:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FTools%2FARM-Templates%2FDataConnectors%2FAzureAD%2FAzureAD.json)
