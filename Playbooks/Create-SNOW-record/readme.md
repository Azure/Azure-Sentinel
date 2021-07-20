# Create-SNOW-record
author: Yaniv Shasha, Benjamin Kovacevic

This playbook will open a Service Now incident when a new incident is opened in Azure Sentinel.<br>
<br>
High severity incident in Azure Sentinel will be synced with Critical priority to SNOW<br>
Medium severity incident in Azure Sentinel will be synced with Moderate priority to SNOW<br>
Low and Informational severity incident in Azure Sentinel will be synced with Planning priority to SNOW<br><br>
## Prerequisites

We will need following data to make SNOW connector:<br>
1. SNOW instance (ex. xyz.service-now.com)<br>
2. Username<br>
3. Password<br>
![SNOW connector requirements](./images/SNOW-connector-requirements.png)<br><br>

## Quick Deployment
**Deploy with incident trigger** (recommended)

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure incident](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-SNOW-record%2Fincident-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov incident](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-SNOW-record%2Fincident-trigger%2Fazuredeploy.json)

**Deploy with alert trigger**

After deployment, you can run this playbook manually on an alert or attach it to an **analytics rule** so it will rune when an alert is created.

[![Deploy to Azure alert](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-SNOW-record%2Falert-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov alert](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-SNOW-record%2Falert-trigger%2Fazuredeploy.json)<br>
<br>
## Post-deployment
Go to Playbook edit mode and fix SNOW connection with data from Prerequisite. <br>
<br>

<strong>Note: This step is necessary only if you are deploying the Playbook using Alert trigger method from above</strong><br>
We will need to assign Azure Sentinel Reader role to the Playbooks Managed Identity:<br>
1. Open Playbook and go to Settings > Identity
2. Click on Azure Role Assignments and then on Add Role Assignment
3. For Scope choose Resource group and make sure that subscription and resource group are where Azure Sentinel and Playbook are deployed. For Role choose Azure Sentinel Reader and click on Save.<br>
<br>
## Screenshots

**Incident Trigger**<br>
![Incident Trigger dark](./incident-trigger/images/dark-Playbook-incident-trigger.png)<br>
![Incident Trigger light](./incident-trigger/images/light-Playbook-incident-trigger.png)<br>
<br>
**Alert Trigger**<br>
![Alert Trigger dark](./alert-trigger/images/dark-Playbook-alert-trigger.png)<br>
![Alert Trigger light](./alert-trigger/images/light-Playbook-alert-trigger.png)<br>
<br>
**Example in ServiceNow**<br>
![Alert Trigger light](./images/in-SNOW.png)<br>
