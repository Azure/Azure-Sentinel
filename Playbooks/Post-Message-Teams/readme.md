#  Post-Message-Teams

Author: Yaniv Shasha

This playbook will post a message in a Microsoft Teams channel when an Alert is created in Azure Sentinel

## Prerequisites

MS teams Account that allow to post messages

## Quick Deployment
**Deploy with incident trigger** (recommended)

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)
 
 
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FPost-Message-Teams%2Fincident-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FPost-Message-Teams%2Fincident-trigger%2Fazuredeploy.json)


**Deploy with alert trigger**

After deployment, you can run this playbook manually on an alert or attach it to an **analytics rule** so it will rune when an alert is created.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FPost-Message-Teams%2Falert-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FPost-Message-Teams%2Falert-trigger%2Fazuredeploy.json)

## Screenshots
**Incident Trigger**
![Incident TriggerL](./incident-trigger/images/designerLight.png)
![Incident TriggerD](./incident-trigger/images/designerDark.png)

**Alert Trigger**
![Alert Trigger](./alert-trigger/images/designerAlertLight.png)

**Microsoft Teams**
![Teams](./images/TeamsDark.png)
