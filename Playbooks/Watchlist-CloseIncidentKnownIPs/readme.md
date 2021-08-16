# Watchlists-CloseIncidentKnownIP
author: Lior Tamir

This playbook levarages Azure Sentinel Watchlists in order to close incidents which include IP addresses considered safe.

For each Ip address included in the alert (entities of type IP):
1. Check if IP is included in watchlist.
    * If IP is in the watchlist, consider the IP saf,. **Add it to Safe IPs array.**
    * If IP is not in the watchlist, meaning that we are not sure it is safe, **Add it to not Safe IPs array.**
2. Add a comment to the incident the list of safe and not safe IPs found.
3. If the not safe list is empty (length == 0), close the incident as Benign Positive.
<br>

## Configurations
* Configure the step "Run query and list results" with the identifiers of the Sentinel workspace where the watchlist is stored.
* The watchlist used in this example has at list one column named **ipaddress** which stores the safe address. See the csv file attached in this folder as an example.
<br><br>

<img src="https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/Watchlist-CloseIncidentKnownIPs/images/designerLight1.png"/><br><br>

<img src="https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/Watchlist-CloseIncidentKnownIPs/images/designerLight2.png"/><br><br>

<img src="https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/Watchlist-CloseIncidentKnownIPs/images/commentLight.png"/><br><br>


[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlist-CloseIncidentKnownIPs%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlist-CloseIncidentKnownIPs%2Fazuredeploy.json)