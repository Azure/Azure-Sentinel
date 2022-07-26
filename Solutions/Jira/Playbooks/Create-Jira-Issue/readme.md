# Create-Jira-Issue
author: Yaniv Shasha, Benjamin Kovacevic

This playbook will open a Jira Issue when a new incident is opened in Azure Sentinel.<br>
<br>
## Prerequisites

We will need following data to make Jira connector:<br>
1. Jira instance (ex. xyz.atlassian.net)<br>
2. Jira API (create API token on https://id.atlassian.com/manage-profile/security/api-tokens)<br>
3. User email<br>
![Jira connector requirements](./images/jira-connector-requirements.png)<br>
<br>
## Quick Deployment
**Deploy with incident trigger** (recommended)

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-Jira-Issue%2Fincident-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-Jira-Issue%2Fincident-trigger%2Fazuredeploy.json)

**Deploy with alert trigger**

After deployment, you can run this playbook manually on an alert or attach it to an **analytics rule** so it will rune when an alert is created.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-Jira-Issue%2Falert-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-Jira-Issue%2Falert-trigger%2Fazuredeploy.json)<br>
<br>
## Post-deployment
Go to Playbook edit mode and fix Jira connection with data from Prerequisite. <br>
When connection is fixed, choose your:
1. Jira Project (where you want to sync Azure Sentinel incidents to) and
2. Issue Type Id (Azure Sentinel incident issue type in Jira - Task, Story, Bug,...).<br>
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
**Example in Jira**<br>
![Alert Trigger light](./images/jira.png)<br>