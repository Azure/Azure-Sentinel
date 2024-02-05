# Get-SentinelAlertsEvidence
Author: Yaniv Shasha

This playbook will Logic will automatically attach alert evidence from Azure Sentinel alerts and send them to an Event Hub that can be consumed by a 3rd party SIEM solution.
<br><br>

# Prerequisites
1.	Create an Event Hub using the article "Create an event hub using Azure portal" <br>
https://docs.microsoft.com/azure/event-hubs/event-hubs-create or use an existing Event Hub.
<br><br>

# Quick Deployment
**Deploy with incident trigger**

After deployment, you can run this playbook manually on an incident or attach this playbook to an **automation rule** so it runs when the incident is created.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-SentinelAlertsEvidence%2Fincident-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-SentinelAlertsEvidence%2Fincident-trigger%2Fazuredeploy.json)


**Deploy with alert trigger**

After deployment, you can run this playbook manually on an alert or attach it to an **automation rule** so it will rune when an alert is created.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-SentinelAlertsEvidence%2Falert-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-SentinelAlertsEvidence%2Falert-trigger%2Fazuredeploy.json)
<br><br>

# Post-deployment
1.	Once the playbook is deployed, Modify the “Run query and list results” actions and point it to your Azure sentinel workspace.<br>
2.	Next, configure the "send event" actions to use your Event Hub that created earlier.<br><br>

# Screenshots
**Incident Trigger**
![Incident Trigger](./images/playbookDark.jpg)