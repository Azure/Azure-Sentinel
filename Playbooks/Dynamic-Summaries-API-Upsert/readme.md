# Dynamic-Summaries-API-Upsert
author: Zhipeng Zhao

This playbook shows how to query Log Analytics data and upload the query result to Sentinel Dynamic Summaries table through Dynamic Summaries REST API.  

## Prerequisites

Before deploying the the playbook you will need 
- create Azure Integration account through Azure portal 
- Have a KQL that renders data for Dynamic Summaries object model  

## Quick Deployment
[Learn more about playbook deployment](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/ReadMe.md)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FDynamic-Summaries-API-Upsert%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FDynamic-Summaries-API-Upsert%2Fazuredeploy.json)

## Post-Deployment
After deployment, the playbook should run automatically, you may go to the Log Analytics to check the result.  You may need to grant this Logic app access to the Destination subscription as a contributor.
