# Watchlists-InformSubowner-IncidentTrigger
author: Lior Tamir

This playbook leverages Microsoft Sentinel Watchlists in order to get the relevant subscription owner contact details, and inform about an ASC alert that occured in that subscription.
It uses Microsoft Teams and Office 365 Outlook as ways to inform the sub owner.

## Prerequisites
Create a Watchlist that this playbook will query:
1.Create an input comma-separated value (CSV) file with the following columns: SubscriptionId, SubscriptionName, OwnerName, OwnerEmail, where each row represents a subscription in an Azure tenant.
2. Upload the table to the Microsoft Sentinel Watchlist area. Make a note of the value you use as the Watchlist Alias, as you'll use it to query this watchlist from the playbook.

Note: This playbook utilizes two features currently in Preview.
* Microsoft Sentinel Watchlists
* Microsoft Sentinel Incident Trigger

![](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Watchlists%20Utilities/Playbooks/Watchlist-InformSubowner-IncidentTrigger/images/designerView.png)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FWatchlists%20Utilities%2FPlaybooks%2FWatchlist-InformSubowner-IncidentTrigger%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FWatchlists%20Utilities%2FPlaybooks%2FWatchlist-InformSubowner-IncidentTrigger%2Fazuredeploy.json)