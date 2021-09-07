# Prompt-User
author: Nicholas DiCola

This playbook will ask the user if they completed the action from the Incident in Azure Sentinel.  If so, it will close the incident and add a comment.  If not, it will post a message to teams for the SOC to investigate and add a comment to the incident.

## Quick Deployment
**Deploy with incident trigger** (recommended)

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FPrompt-User%2Fincident-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FPrompt-User%2Fincident-trigger%2Fazuredeploy.json)

**Deploy with alert trigger**

After deployment, you can run this playbook manually on an alert or attach it to an **analytics rule** so it will rune when an alert is created.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FPrompt-User%2Falert-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)]("https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FPrompt-User%2Falert-trigger%2Fazuredeploy.json)


## Prerequisites

- [This](https://www.linkedin.com/pulse/3-ways-locate-microsoft-team-id-christopher-barber-/) blog shows some simple methods to get the Team Id.  You will need the Team Id and Channel Id.


## Screenshots
**Incident Trigger**<br>
![Incident Trigger](./incident-trigger/images/designerLight.png)<br>
**Alert Trigger**<br>
![Alert Trigger](./alert--trigger/images/Prompt-User_alert.png)<br>