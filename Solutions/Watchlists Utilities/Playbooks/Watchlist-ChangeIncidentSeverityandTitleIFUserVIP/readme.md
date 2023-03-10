# Watchlist-ChangeIncidentSeverityandTitleIFUserVIP

author: Yaniv Shasha


This playbook leverages Microsoft Sentinel Watchlists in order to adapt the incidents severity which include User entity and check it against VIP user list


## Logical flow to use this playbook
For each User account included in the incident or alert (entities of type User):
1. Check if User is included in the watchlist.
2. If user is in the watchlist:
a. change the incident severity to Critical  
b. Modify the incident title that include the User name and the text- **VIP User!!!**


# Prerequisites

None.

# Quick Deployment
**Deploy with incident trigger** (recommended)

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FWatchlists%20Utilities%2FPlaybooks%2FWatchlist-ChangeIncidentSeverityandTitleIFUserVIP%2Fincident-trigger%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FWatchlists%20Utilities%2FPlaybooks%2FWatchlist-ChangeIncidentSeverityandTitleIFUserVIP%2Fincident-trigger%2Fazuredeploy.json)

**Deploy with alert trigger**

After deployment, you can run this playbook manually on an alert or attach it to an **analytics rule** so it will rune when an alert is created.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FWatchlists%20Utilities%2FPlaybooks%2FWatchlist-ChangeIncidentSeverityandTitleIFUserVIP%2Falert-trigger%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FWatchlists%20Utilities%2FPlaybooks%2FWatchlist-ChangeIncidentSeverityandTitleIFUserVIP%2Falert-trigger%2Fazuredeploy.json)

# Post-deployment
1. Assign Microsoft Sentinel Contributor role to the Playbook's Managed Identity

## Screenshots
**Incident Trigger**
![Incident Trigger](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Watchlists%20Utilities/Playbooks/Watchlist-ChangeIncidentSeverityandTitleIFUserVIP/incident-trigger/images/incidentTrigger-light.png)

![Incident Trigger](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Watchlists%20Utilities/Playbooks/Watchlist-ChangeIncidentSeverityandTitleIFUserVIP/incident-trigger/images/incidentTrigger-dark.png)

**Alert Trigger**
![Alert Trigger](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Watchlists%20Utilities/Playbooks/Watchlist-ChangeIncidentSeverityandTitleIFUserVIP/alert-trigger/images/alertTrigger-light.png)

![Alert Trigger](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Watchlists%20Utilities/Playbooks/Watchlist-ChangeIncidentSeverityandTitleIFUserVIP/alert-trigger/images/alertTrigger-dark.png)