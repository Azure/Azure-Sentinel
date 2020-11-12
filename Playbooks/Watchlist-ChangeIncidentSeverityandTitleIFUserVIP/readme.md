# Watchlist-ChangeIncidentSeverityandTitleIFUserVIP
author: Yaniv Shasha

This playbook leverages Azure Sentinel Watchlists in order to adapt the incidents severity which include User entity and check it against VIP user list

For each User account included in the alert (entities of type User):
1. Check if User is included in watchlist.
    * If user is in the watchlist, change the incident severity to Critical  2. Add a comment to the incident the list of safe and not safe IPs found.
	2. Modify the incident title that include the User name and the text. **VIP User!!!**
	<br>

## Configurations
* Configure the step "Run query and list results" with the identifiers of the Sentinel workspace where the watchlist is stored.
* The watchlist used in this example has at list one column named **Name** which stores the safe address. See the csv file attached in this folder as an example.
<br><br>
Overall:
<img src="https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/Watchlist-ChangeIncidentSeverityandTitleIFUserVIP/images/designerView.png"/><br><br>
For each IP:
<img src="https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/Watchlist-ChangeIncidentSeverityandTitleIFUserVIP/images/foreach.png"/><br><br>


<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlist-ChangeIncidentSeverityandTitleIFUserVIP%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlist-ChangeIncidentSeverityandTitleIFUserVIP%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>