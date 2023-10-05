# Dynamic-Summaries-API-Upsert
author: Zhipeng Zhao

This playbook shows how to query Log Analytics data and upload the query result to Sentinel Dynamic Summaries table through Dynamic Summaries REST API.  

## Prerequisites

Before deploying the playbook you will need 
- [Create Azure Integration account through Azure portal](https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/logic-apps/logic-apps-enterprise-integration-create-integration-account.md#tab/azure-portal).  Integration account should be in the same region as Logic App. And integration account must be in either Basic or Standard pricing tier.
- Have a KQL that renders data for [Dynamic Summaries object models](https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/Dynamic-Summaries-API-Upsert/DynamicSummaries_API_Models.pdf).
- Logic App and Log Analytics Workspace for Dynamic Summaries should be in the same Azure resource group.
- Finally user must be a subscription owner to deploy the playbook template.

## Quick Deployment
[Learn more about playbook deployment](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/ReadMe.md)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FDynamic-Summaries-API-Upsert%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FDynamic-Summaries-API-Upsert%2Fazuredeploy.json)

## Post-Deployment
After deployment, the playbook will run automatically, it may fail due to permission issues.  You need to perform one action:
- You need to authorize the API Connections, going to API connections, selecting the API connection, selecting Edit API connection. then clicking Authorize button at the bottom.
