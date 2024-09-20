# Get-ASCRecommendations

author: Nicholas DiCola

This playbook will take each Host entity and If its an Azure Resource, query ASC API to get any ASC recommendations.  It will add a tag and comment if any unhealthy recommendations are found for the resource.

## Quick Deployment
**Deploy with incident trigger** (recommended)

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-ASCRecommendations%2Fincident-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-ASCRecommendations%2Fincident-trigger%2Fazuredeploy.json)

**Deploy with alert trigger**

After deployment, you can run this playbook manually on an alert or attach it to an **analytics rule** so it will rune when an alert is created.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-ASCRecommendations%2Falert-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-ASCRecommendations%2Falert-trigger%2Fazuredeploy.json[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](

## Prerequisites

- This playbook uses a managed identity to access the API.  You will need to add the managed identity that is created by the logic app to the subscripton(s) of management group with Security Reader permissions.

## Screenshots
**Incident Trigger**<br>
![Incident Trigger](./incident-trigger/images/Get-ASCRecommendations_incident.png)<br>
**Alert Trigger**<br>
![Alert Trigger](./alert-trigger/images/Get-ASCRecommendations_alert.png)<br>