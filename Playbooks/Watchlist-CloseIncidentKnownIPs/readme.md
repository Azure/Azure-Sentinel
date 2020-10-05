# Watchlists-CloseIncidentKnownIP
author: Lior Tamir

This playbook levarages Azure Sentinel Watchlists in order to close incidents which include only safe Ip addresses.

For each Ip address that this alert includes (entities of type Ip):
1. Check if Ip is included in watchlist.
    * If Ip is in the watchlist, means it safe. **Add it to Safe Ips array.**
    * If Ip is not in the watchlist, meand we are not sure it is safe. **Add it to not Safe Ips array.**
2. Add as a comment to the incident the list of safe and not safe IPs found.
3. If the not safe list is empty (length == 0), close the incident as Benign Positive.
<br>

## Configurations
* Configure the step "Run query and list results" with the identifiers of the Sentinel workspace where the watchlist is stored.
* The watchlist used in this example has at list one column named **ipaddress** which stores the safe address. See the csv file attached in this folder as an example.
<br><br>
Overall:
<img src="https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlists-CloseIncidentKnownIP/images/designerView.png"/><br><br>
For each IP:
<img src="https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlists-CloseIncidentKnownIP/images/ForEach.png"/><br><br>
Update incident by the results:
<img src="https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlists-CloseIncidentKnownIP/images/end.png"/><br><br>


<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlists-CloseIncidentKnownIP%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlists-CloseIncidentKnownIP%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>
