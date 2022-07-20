#  Watchlist-Add-UserToWatchList

Author: Yaniv Shasha
<br><br>

This playbook will add a User entity to a new or existing watchlist.
<br><br> 

## Logical flow to use this playbook

	1. The analyst finished investigating an incident and one of its findings is a suspicious user entity.
	2. The analyst wants to enter this entity into a watchlist (can be from block list type or allowed list).
	3. This playbook will run as a manual trigger from the full incident blade or the investigation graph blade, or automatically, and will add host to the selected watchlist.

# Prerequisites

None.<br><br>

# Quick Deployment
**Deploy with incident trigger** (recommended)

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlist-Add-UserToWatchList%2Fincident-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlist-Add-UserToWatchList%2Fincident-trigger%2Fazuredeploy.json)

**Deploy with alert trigger**

After deployment, you can run this playbook manually on an alert or attach it to an **analytics rule** so it will rune when an alert is created.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlist-Add-UserToWatchList%2Falert-trigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlist-Add-UserToWatchList%2Falert-trigger%2Fazuredeploy.json)
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