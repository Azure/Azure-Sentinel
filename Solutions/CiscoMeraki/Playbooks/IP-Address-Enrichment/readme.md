# Cisco Meraki IP Address Enrichment Playbook

![meraki](../../Connector/MerakiConnector/logo.jpg)

## Summary
 When a new Microsoft Sentinel incident is created, this playbook gets triggered and performs the below actions:
 1. Fetches a list of potentially malicious IP addresses.
 2. For each IP address in the list, checks if the IP address is blocked by L3 firewall rule or L7 firewall rule in MX network.
  - If IP address is part of both L3 firewall rule and L7 firewall rule but not blocked by either of the rules, then Incident Comment is created saying IP address allowed by firewall.
  - If IP address is part of either L3 firewall rule or L7 firewall rule and blocked by the rule, then Incident Comment is created saying IP address is blocked.
  - If IP address is not part of either L3 firewall rule or L7 firewall rule, then Incident Comment is created saying IP address not found in any rule.

![Meraki](./Images/PlaybookDesignerLight.jpg)

![Meraki](./Images/PlaybookDesignerDark.jpg)


 ## Pre-requisites for deployment
1. Deploy the Cisco Meraki Custom Connector before the deployment of this playbook under the same subscription and same resource group. Capture the name of the connector during deployment.
2. Cisco Meraki API Key should be known to establish a connection with Cisco Meraki Custom Connector. [Refer here](https://developer.cisco.com/meraki/api-v1/#!getting-started/authorization)
3. Organization name should be known. [Refer here](https://developer.cisco.com/meraki/api-v1/#!getting-started/find-your-organization-id) 


 ## Deployment Instructions
 1. Deploy the playbook by clicking on the "Deploy to Azure" button. This will take you to deploy an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCiscoMeraki%2FPlaybooks%2FIP-Address-Enrichment%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCiscoMeraki%2FPlaybooks%2FIP-Address-Enrichment%2Fazuredeploy.json)


 2. Fill in the required parameters for deploying the playbook.

 | Parameter  | Description |
| ------------- | ------------- |
| **Playbook Name** | Enter the playbook name without spaces |
| **Cisco Meraki Connector name** | Enter the name of Cisco Meraki custom connector without spaces |
| **Organization Name** | Enter organization name |


# Post-Deployment Instructions 
## a. Authorize API connection
* Once deployment is complete, go under deployment details and authorize Cisco Meraki connection. 
1.  Click the Cisco Meraki connection
2.  Click **Edit API connection**
3.  Enter API Key
4.  Click Save

## b. Configurations in Sentinel
- In Microsoft sentinel analytical rules should be configured to trigger an incident with IP addresses. 
- Configure the automation rules to trigger the playbook.


# Playbook steps explained
## When Microsoft Sentinel incident creation rule is triggered
Captures potentially malicious or malware IP addresses incident information.

## Entities - Get IPs
Get the list of IPs as entities from the Incident.

## Check if Organization exists
 *  If organization name exists in list of organizations associated with the account, then get list of networks associated with the organization. 
 *  If organization name does not exist, then terminate with the error that organization not found.

## For each malicious IP received from the incident
 - Checks if the IP address is part of L3 firewall rule or L7 firewall rule in MX network.
   - If IP address is part of both L3 firewall rule and L7 firewall rule but not blocked by either of the rules, then Incident Comment is created saying IP address allowed by firewall.
   - If IP address is part of either L3 firewall rule or L7 firewall rule and blocked by the rule, then Incident Comment is created saying IP address is blocked.
   - If IP address is not part of either L3 firewall rule or L7 firewall rule, then Incident Comment is created saying IP address not found in any rule.
 - Add incident Comment from all the cases.

## Incident comment 
![meraki](./Images/IncidentCommentLight.jpg)

![meraki](./Images/IncidentCommentDark.jpg)