# ThreatX Logic Apps Custom connector

This custom connector connects to ThreatX WAF service end point to runs any ThreatX waf supported API get/post calls and gives response back in json format.
### Authentication methods this connector supports

*  Token generation via api key

### Prerequisites for deploying Custom Connector
1. API key. To get API Key, login into your ThreatX cloud instance dashboard and navigate to Settings --> API Key --> Add API key.


## Actions supported by ThreatX Cloud custom connector

| Component | Description |
| --------- | -------------- |
| **Login/Generate Token** | Allows for authorization and access to API commands using an API token |
| **Token Refresh** | Uses a valid, unexpired API access token to issue a new access token with a refreshed expiration time |
| **Fetch update blocklist/blacklist/whitelist** | Allows managing of IP addresses within the WAF Blacklist, Blocklist, and Whitelist of the specified tenant |
| **Fetch update Custom Rules** | lists/Update all customer rules for the specified tenant, and their details |
| **Get Entities** | Fetch the list of Entities within the specified query criteria |
| **Get Event Log Detail** | Fetch the detailed log of attacks happens at WAF end |


### Deployment instructions 
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FThreatXCloud%2FPlaybooks%2FCustomConnector%2FThreatXCustomConnector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FThreatXCloud%2FPlaybooks%2FCustomConnector%2FThreatXCustomConnector%2Fazuredeploy.json)

## Usage Examples
* Get details of attacks and add to Sentinel incident comment through playbook
* Block Ip or URL through playbook at WAF end
* Fetch the list of blocked or allowed IP & URL through playbook
