# Enrich-AzureResourceGraph-Incident

This logicapp calls Enrich-AzureResourceGraph to comment Sentinel Incident based on ResourceGraph data

## Quick Deployment

After deployment,
* Allow logicapp managed identity to update incident by adding IAM role [Sentinel Responder or above](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#microsoft-sentinel-responder)
* attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FEnrich-AzureResourceGraph-Incident%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FEnrich-AzureResourceGraph-Incident%2Fazuredeploy.json)

## Prerequisites

* Enrich-AzureResourceGraph logicapp
* Adapt query to your context

## Screenshots
![Enrich-AzureResourceGraph-Incident](./images/Enrich-AzureResourceGraph-Incident.png)

## Workflow explained

1. Azure Sentinel incident trigger
2. Get Hosts entities
3. For each host, call Enrich-AzureResourceGraph
4. Add comment and tag found/notfound depending on output
