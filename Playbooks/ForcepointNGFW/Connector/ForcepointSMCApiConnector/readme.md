# Forcepoint SMC Logic Apps Custom Connector

![Forcepoint](/Playbooks/logo.jpg)<br>

# Overview
This custom connector connects to Forcepoint SMC (Security Management Center) service endpoint and performs defined automated actions on the Forcepoint NGFW (Next Generation Firewall).

# Authentication
*  API key is required for Login API.

# Actions supported by Forcepoint SMC custom connector
| Component | Description |
| --------- | -------------- |
| **Login** | Logs in to the Forcepoint SMC server.|
| **Get policy Name** | Searches for security policy by policy name in the firewall.|
| **Logout** | Logs out of Forcepoint SMC server. |
| **Delete policy rule by IP or URL** | Deletes security rule if IP or URL is unblocked. |
| **Get IP address list** | Gets the list of all IPs if the filter is empty or Gets a list of IPs by filter value. |
| **Create IP list name** |Creates  IP list to add the IP address.|
| **Add IP address into IP list** | Adds IP address to IP list. |
| **Get policy rule by IP or URL** | Filters IP or URL from security policy rule.|
| **Unlock policy** | Unlocks the policy if it is locked by an admin user.|
| **Delete IP address** | Deletes the IP address from SMC. |
| **Get URL list** |Gets a list of all URLs if the filter is empty or Gets a list of URLs by filter value. |
| **Create URL list**|Creates a list of URLs. |
| **Delete URL from URL list**| Deletes URL from URL List.|
| **Upload policy**|Uploads the policy after adding IP or URL into policy. |
|**Create policy rule in firewall**|Creates policy rule for any IP or URL sources. |
| **Get complete policy rule details**| Gets complete policy details by rule name.|
| **Find IP or URL in SMC**| Searches IP or URL in Forcepoint SMC.|
|**Get IP address**|Gets list of all IP addresses in IP List.|
|**Get URL from URL List**|Gets list of all URLs from URL List.|
|**Upload URL to URL List**|Updates URL to URL List.|
|**Get Host**|Gets host by IP address or list of IP address.|


# Prerequisites for deploying Forcepoint SMC Custom Connector
 * Forcepoint SMC service endpoint should be known. (e.g.  https://{forcepointdomain:PortNumber/})


# Deploy Forcepoint SMC Custom Connector
Click on the below button to deploy Forcepoint SMC Custom Connector in your Azure subscription.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FForcepointNGFW%2FForcepointSMCApiConnector%2Fazuredeploy.json)
 [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FForcepointNGFW%2FForcepointSMCApiConnector%2Fazuredeploy.json) 


# Deployment Instructions 
1. Deploy the Forcepoint SMC custom connector by clicking on the "Deploy to Azure" button. This will take you to deploy an ARM Template wizard.
2. Fill in the required parameters for deploying Forcepoint SMC custom connector.

## Deployment Parameters

| Parameter  | Description |
| ------------- | ------------- |
| **Custom Connector Name** | Enter the name of Forcepoint SMC custom connector without spaces. |
| **Service End Point** | Enter the Forcepoint SMC Service End Point. |

**NOTE: Forcepoint SMC admin must grant privileges to Forcepoint API users, so users can have access to manage security policy rules.**




