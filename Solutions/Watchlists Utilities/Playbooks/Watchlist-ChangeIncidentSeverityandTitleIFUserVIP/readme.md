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

# Scenario based changes
1.The erroneous behaviour happens because same user account has been used to create the VIP User watchlist in one of the scenario
please follow the below steps

**Step1:**
Set variable: “Set watchlist items”

{

    "inputs": {

        "name": "WatchlistItemsArray",

        "value": "@body('Parse_JSON')?['properties']?['watchlistItems']"

    }

}


**Step2:**

Set variable: “Set UPN”

 

{

    "inputs": {

        "name": "UPN",

        "value": "@{items('For_each_2')?['properties.itemsKeyValue']?['User Principal Name']}"

    }

}
variables(‘UPN’) contains ‘Accounts Name’


##Screenshots

![image](https://github.com/Azure/Azure-Sentinel/assets/139563098/f0414435-44a9-4481-8b44-c7ae37f00f7e)

expression": {
                                    "and": [
                                        {
                                            "contains": [
                                                "@variables('UPN')",
                                                "@items('For_each')?['Name']"
                                            ]
                                        }
                                    ]
                                },




![image](https://github.com/Azure/Azure-Sentinel/assets/139563098/d41c594b-7976-40d1-9bd5-6be452267f0f)


![image](https://github.com/Azure/Azure-Sentinel/assets/139563098/280eab55-b653-4dc2-9cfe-aee20f95f0b7)


![image](https://github.com/Azure/Azure-Sentinel/assets/139563098/ad6f09da-485d-4633-8fdc-d45e2f1aec53)


![image](https://github.com/Azure/Azure-Sentinel/assets/139563098/5d7041da-6d50-490e-ad0a-9da746166083)











