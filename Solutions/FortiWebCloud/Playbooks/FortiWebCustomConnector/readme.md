# FortiWeb WAF Logic Apps Custom connector

This custom connector connects to Fortiweb WAF service end point to runs any fortiweb waf supported API get/post calls and gives response back in json format.
### Authentication methods this connector supports

*  API Key authentication

### Prerequisites for deploying Custom Connector
1. FortiWeb Cloud host end point or url should be known(ex : api.fortiweb-cloud.com)
2. API key. To get API Key, login into your FortiWeb cloud instance dashboard and navigate to Global --> system settings --> API Key.


## Actions supported by FortiWeb Cloud custom connector

| Component | Description |
| --------- | -------------- |
| **Get URL Access** | Fetch the list of URL Blocked or Allowed at WAF |
| **Update URL Access** | Update the New URL with the existing one with allowed or blocked traffic at WAF |
| **Get IP Protection** | Fetch the list of IP Blocked or Allowed at WAF |
| **Update IP Protection** | Update the New IP with the existing one with allowed or blocked traffic at WAF |
| **Get Attack Logs List** | Fetch the list of attacks happens at WAF end |
| **Get Attack Log Detail** | Fetch the details of attacks happens at WAF end |


### Deployment instructions 
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required paramteres:
    * Custom Connector Name : Enter the Custom connector name (ex:FortiWebCloud)
    * Fortiweb cloud Host URL: Enter the Fortiweb cloud URL or Host (ex: api.fortiweb-cloud.com)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FFortiWebCloud%2FPlaybooks%2FFortiWebCloudCustomConnector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FFortiWebCloud%2FPlaybooks%2FFortiWebCloudCustomConnector%2Fazuredeploy.json)

## Usage Examples
* Get details of attacks and add to Sentinel incodent comment through playbook
* Block Ip or URL through playbook at WAF end
* Fetch the list of blocked or allowed IP & URL through playbook
