# Watchlists-CloseIncidentKnownIP
author: Lior Tamir

This playbook levarages Microsoft Sentinel Watchlists in order to close incidents which include IP addresses considered safe.

For each Ip address included in the alert (entities of type IP):
1. Check if IP is included in watchlist.
    * If IP is in the watchlist, consider the IP safe, **Add it to Safe IPs array.**
    * If IP is not in the watchlist, meaning that we are not sure it is safe, **Add it to not Safe IPs array.**
2. Add a comment to the incident the list of safe and not safe IPs found.
3. If the not safe list is empty (length == 0), close the incident as Benign Positive.

## Prerequisites
<a href='https://docs.microsoft.com/azure/sentinel/watchlists?WT.mc_id=Portal-fx#create-a-new-watchlist'>Create a watchlist</a> for safe IPs with ip column named 'ipaddress' (can be changed in 'Run query' step). Watchlist should be located in the same workspace of the incidents.

## Configurations
* Configure the step "Run query and list results" with the identifiers of the Sentinel workspace where the watchlist is stored.
* Configure the identity used in the "Run query and list results" step with the Log Analytics Reader RBAC role on the Microsoft Sentinel resource group.
* Configure the Managed Idenitty of the Logic App with the Microsoft Sentinel Responder RBAC role on the Microsoft Sentinel resource group.
* The watchlist used in this example has at list one column named **ipaddress** which stores the safe address. See the csv file attached in this folder as an example.

![](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Watchlists%20Utilities/Playbooks/Watchlist-CloseIncidentKnownIPs/images/designerLight1.png)

![](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Watchlists%20Utilities/Playbooks/Watchlist-CloseIncidentKnownIPs/images/designerLight2.png)

![](https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Watchlists%20Utilities/Playbooks/Watchlist-CloseIncidentKnownIPs/images/commentLight.png)


[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FWatchlists%20Utilities%2FPlaybooks%2FWatchlist-CloseIncidentKnownIPs%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FWatchlists%20Utilities%2FPlaybooks%2FWatchlist-CloseIncidentKnownIPs%2Fazuredeploy.json)
