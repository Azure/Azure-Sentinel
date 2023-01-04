# Cisco Meraki Logic Apps Custom Connector and Playbook Templates

![meraki](./Connector/MerakiConnector/logo.jpg)


## Table of Contents

1. [Overview](#overview)
1. [Deploy Custom Connector + 5 Playbook templates](#deploy)
1. [Authentication](#authentication)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)
1. [References](#references)
1. [Limitations](#limitations)


<a name="overview">

# Overview
Cisco Meraki connector connects to Cisco Meraki Dashboard API service endpoint and programmatically manages and monitors Meraki networks at scale.


<a name="deploy">

# Deploy Custom connector + 5 Playbook templates
This package includes:
* Custom connector for Cisco Meraki.
* Five playbook templates leverage Cisco Meraki custom connector.

You can choose to deploy the whole package : Connector + all five playbook templates, or each one seperately from it's specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoMeraki%2FConsolidatedTemplate.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCiscoMeraki%2FConsolidatedTemplate.json)


# Cisco Meraki documentation 

<a name="authentication">

# Authentication
API Key Authentication

<a name="prerequisites">

# Prerequisites for using and deploying Custom connector + 5 playbooks
1. Cisco Meraki API Key should be known to establish a connection with Cisco Meraki Custom Connector. [Refer here](https://developer.cisco.com/meraki/api-v1/#!getting-started/authorization)
2. Cisco Meraki Dashboard API service endpoint should be known. (e.g. https://{CiscoMerakiDomain}/api/{VersionNumber}) [Refer here](https://developer.cisco.com/meraki/api-v1/#!schema)
3. Organization name should be known. [Refer here](https://developer.cisco.com/meraki/api-v1/#!getting-started/find-your-organization-id) 
4. Network name should be known.[Refer here](https://developer.cisco.com/meraki/api-v1/#!getting-started/find-your-network-id)
5. Network Group Policy name should be known. [Refer here](https://developer.cisco.com/meraki/api-v1/#!get-network-group-policy)

<a name="deployment">

# Deployment instructions 
1. Deploy the Custom connector and playbooks by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters for deploying custom connector and playbooks

| Parameter  | Description |
| ------------- | ------------- |
|**For Playbooks**|                 |
|**Block Device Client Playbook Name** | Enter the Block Device Client playbook name without spaces |
|**Block IP Address Playbook Name** | Enter the Block IP Address playbook name without spaces |
|**Block URL Playbook Name**|Enter the Block URL playbook name without spaces|
|**Enrichment IP Address Playbook Name**|Enter the IP Address Enrichment playbook name without spaces|
|**Enrichment URL Playbook Name**|Enter the URL Enrichment playbook name without spaces|
|**Organization Name**|Enter the name of Organization|
|**Network Name**  | Enter the name of Network | 
|**Group Policy** | Enter the name of Group Policy |
|**For Custom Connector**|                             |
|**Cisco Meraki Connector Name**|Enter the name of Cisco Meraki custom connector without spaces|
|**Service EndPoint**|Enter the Cisco Meraki Service End Point|

<a name="postdeployment">

# Post-Deployment Instructions 
## a. Authorize API connections
* Once deployment is complete, go under deployment details and authorize Cisco Meraki connection. 
1.  Click the Cisco Meraki connection
2.  Click **Edit API connection**
3.  Enter API Key
4.  Click Save

## b. Configurations in Sentinel
1. In Microsoft sentinel analytical rules should be configured to trigger an incident with risky IP address, URL or Hosts. 
2. Configure the automation rules to trigger the playbooks.


<a name="references">

#  References
 - [Cisco Meraki Dashboard API](https://dashboard.meraki.com/api_docs) 
 - [Content Filtering - Cisco Meraki](https://documentation.meraki.com/MX/Content_Filtering_and_Threat_Protection/Content_Filtering#Content_Filtering_Rule_Priority)
 - [Layer 3 and 7 Firewall Processing Order - Cisco Meraki](https://documentation.meraki.com/General_Administration/Cross-Platform_Content/Layer_3_and_7_Firewall_Processing_Order)

Connector
* [Cisco Meraki Custom Connector](/Connector/MerakiConnector/readme.md)

Playbooks
* [Block Device Client - Cisco Meraki](/Playbooks/Block-Device-Client/readme.md)
* [Block IP Address - Cisco Meraki](/Playbooks/Block-IP-Address/readme.md)
* [Block URL - Cisco Meraki](/Playbooks/Block-URL/readme.md)
* [Enrichment IP Address - Cisco Meraki](/Playbooks/IP-Address-Enrichment/readme.md)
* [Enrichment URL - Cisco Meraki](/Playbooks/URL-Enrichment/readme.md)


<a name="limitations">

#  Known Issues and Limitations
 - Need to authorize the api connections after deploying the playbooks.
 - For Block Device Client Playbook, While configuring the rule in Microsoft Sentinel - Device Client MAC needs to be mapped with hostname in Host entity.