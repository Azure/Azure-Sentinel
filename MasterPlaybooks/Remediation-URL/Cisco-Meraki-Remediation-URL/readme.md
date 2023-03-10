# Cisco Meraki Block URL Nested Remediation Playbook

## Summary
 When this playbook gets triggered and it performs the below actions:
 1. Gets a list of potentially malicious URLs.
 2. For each URL in the list, checks if the URL is blocked by the network of the organization.
  - If URL is allowed by the network, then incident comment is created saying URL is allowed.
  - If URL is blocked by the network, then incident comment is created saying URL is blocked.
  - If URL is not blocked by the network and not part of the network, that URL is blocked by playbook.


 ## Pre-requisites for deployment
1. Deploy the Cisco Meraki Custom Connector before the deployment of this playbook under the same subscription and same resource group. Capture the name of the connector during deployment.
2. Cisco Meraki API Key should be known to establish a connection with Cisco Meraki Custom Connector. [Refer here](https://developer.cisco.com/meraki/api-v1/#!getting-started/authorization)
3. Organization name should be known. [Refer here](https://developer.cisco.com/meraki/api-v1/#!getting-started/find-your-organization-id) 
4. Network name should be known.[Refer here](https://developer.cisco.com/meraki/api-v1/#!getting-started/find-your-network-id)

### Deploy Custom Connector

To deploy Cisco Meraki Custom connector click on the below button.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoMeraki%2FConnector%2FMerakiConnector%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoMeraki%2FConnector%2FMerakiConnector%2Fazuredeploy.json)

 ## Deployment Instructions
 1. Deploy the playbook by clicking on the "Deploy to Azure" button. This will take you to deploy an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Ftree%2Fmaster%2FMasterPlaybooks%2FRemediation-URL%2FCisco-Meraki-Remediation-URL%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Ftree%2Fmaster%2FMasterPlaybooks%2FRemediation-URL%2FCisco-Meraki-Remediation-URL%2Fazuredeploy.json)


 2. Fill in the required parameters for deploying the playbook.

 | Parameter  | Description |
| ------------- | ------------- |
| **Playbook Name** | Enter the playbook name without spaces |
| **Cisco Meraki Connector name**|Enter the name of Cisco Meraki custom connector without spaces |
| **Organization Name** | Enter organization name |
| **Network Name**| Enter network name | 


# Post-Deployment Instructions 
##  Authorize API connection
Once deployment is complete, go under deployment details and authorize Cisco Meraki connection. 
1.  Click the Cisco Meraki connection
2.  Click **Edit API connection**
3.  Enter API Key
4.  Click Save

# Playbook steps explained
## When the playbook is triggered
  The playbook receives list of malicious URLs as the input.


## Compose image to add in the incident
This action will compose the Cisco Meraki image to add to the incident comments.

## Check if Organization exists
 *  If organization name exists in list of organizations associated with the account, then return organization. 
 *  If organization name does not exist, then terminate with the error that organization not found.

 ## Check if network exists
  *  If network name exists in list of networks associated with the organization, then return network associated with the organization. 
 *  If network name does not exist, then terminate with the error that network not found.

## For each malicious URL received from the incident
 - Checks if the URL is blocked or allowed by the network of the organization.
   - If URL is allowed by the network then incident comment is created saying URL is allowed using content filtering.
   - If URL is blocked by network then incident comment is created saying URL is blocked using content filtering.
   - If URL is not part of the network, then such URL is blocked by playbook using content filtering. Incident Comment is created saying URL blocked by playbook.
   - Responses from all the cases are combined.

## Response from playbook is sent to master playbook to generate incident comments.

