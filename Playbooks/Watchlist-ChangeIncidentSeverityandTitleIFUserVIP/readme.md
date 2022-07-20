# Watchlist-ChangeIncidentSeverityandTitleIFUserVIP

author: Yaniv Shasha
<br><br>

This playbook leverages Azure Sentinel Watchlists in order to adapt the incidents severity which include User entity and check it against VIP user list
<br><br>

## Logical flow to use this playbook
For each User account included in the incident or alert (entities of type User):
1. Check if User is included in the watchlist.
2. If user is in the watchlist:<br>
a. change the incident severity to Critical  
b. Modify the incident title that include the User name and the text- **VIP User!!!**
<br>

# Prerequisites

None.<br><br>

# Quick Deployment
**Deploy with incident trigger** (recommended)

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlist-ChangeIncidentSeverityandTitleIFUserVIP%2Fincident-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlist-ChangeIncidentSeverityandTitleIFUserVIP%2Fincident-trigger%2Fazuredeploy.json)

**Deploy with alert trigger**

After deployment, you can run this playbook manually on an alert or attach it to an **analytics rule** so it will rune when an alert is created.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlist-ChangeIncidentSeverityandTitleIFUserVIP%2Falert-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlist-ChangeIncidentSeverityandTitleIFUserVIP%2Falert-trigger%2Fazuredeploy.json)
<br><br>

# Post-deployment
1. Assign Microsoft Sentinel Contributor role to the Playbook's Managed Identity

<br><br>

## Screenshots
**Incident Trigger**<br>
![Incident Trigger](./incident-trigger/images/incidentTrigger-light.png)<br>
![Incident Trigger](./incident-trigger/images/incidentTrigger-dark.png)<br><br><br>
**Alert Trigger**<br>
![Alert Trigger](./alert-trigger/images/alertTrigger-light.png)<br>
![Alert Trigger](./alert-trigger/images/alertTrigger-dark.png)<br>