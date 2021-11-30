# Watchlists-InformSubowner-IncidentTrigger
author: Lior Tamir

This playbook levarages Azure Sentinel Watchlists in order to get the relevant subscription owner contact details, and inform about an ASC alert that occured in that subscription.
It uses Microsoft Teams and Office 365 Outlook as ways to inform the sub owner.


Note: This playbook utilizes two features currently in Preview.
* Azure Sentinel Watchlists
* Azure Sentinel Incident Trigger
<br><br>

<img src="https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/Watchlist-InformSubowner-IncidentTrigger/images/designerView.png"/><br><br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlist-InformSubowner-IncidentTrigger%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlist-InformSubowner-IncidentTrigger%2Fazuredeploy.json)