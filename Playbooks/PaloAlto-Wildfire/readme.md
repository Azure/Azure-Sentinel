# Palo Alto WildFire Logic Apps Custom Connector and Playbook templates

![wildfire](./wildfirelogo.png)

## Table of Contents

1. [Overview](#overview)
1. [Prerequisites](#prerequisites)
1. [Authentication](#authentication)
1. [Deploy WildFire custom connector and 3 playbook templates](#deployall) 
1. [Deployment Instructions](#instructions)
1. [Post-Deployment Instructions](#postdeployment)
1. [References](#references)
1. [Limitations](#limitations)

<a name="overview">

# Overview 

Palo Alto Wildfire Next Generation Firewall is used to fetch the verdict information of the URL and filehash, hence providing protection from malware and malicious URLs.

<a name="prerequisites">

# Prerequisites for deploying WildFire custom connector and 3 playbook ARM templates
- Palo Alto Pan-OS Custom Connector needs to be deployed prior to the deployment of playbooks under the same subscription as well as same resource group and capture the name of the connector during the deployment.
- Wildfire API end point should be known. ([WildFire Console](https://wildfire.paloaltonetworks.com))
- Wildfire API key should be known. ([Generate WildFire API Key](https://wildfire.paloaltonetworks.com/wildfire/dashboard)).
- Create the security policy rule on PAN-OS VM and capture rule name.

<a name="authentication">

# Authentication
WildFire Custom Connector supports: API Key Authentication 


<a name="deployall">

# Deploy Wildfire custom connector and 3 playbook ARM templates
This package includes:
* Custom connector for WildFire.
* Three playbook templates leveraging wildfire custom connector.

You can choose to deploy the whole package: connector and all three playbook templates together, or each one separately from its specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2PaloAlto-Wildfire%2FazuredeployConsoildatedTemplate.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FPaloAlto-Wildfire%2FazuredeployConsoildatedTemplate.json)

<a name="instructions">

# Deployment Instructions 
- Deploy the WildFire custom connector and Playbooks by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
- Fill in the required parameters for deploying WildFire custom connector and playbooks.


## Deployment Parameters

| Parameter  | Description |
| ------------- | ------------- |
| **Filehash Enrichment Playbook Name**  | Enter the Filehash Enrichment Playbook Name |
| **Block URL Playbook Name** | Enter the Block URL Playbook Name |
| **Block URL From Teams Playbook Name** | Enter the Block URL From Teams Playbook Name |
| **Wildfire Custom Connector Name** | Enter the name of Palo Alto WildFire custom connector |
| **Wildfire Service End Point** | Enter the Service End Point of Wildfire API [WildFire Console](https://wildfire.paloaltonetworks.com)|
| **Wildfire API Key**  | Enter the WildFire API Key| 
| **Notification Email** | Enter the DL or SOC email address for receiving filehash report|
| **PAN-OS Custom Connector Name**  | Enter the Palo Alto PAN-OS custom connector name  |
| **Security Policy Rule** | Enter the Security Policy Rule which is created in PAN-OS |

<a name="postdeployment">

# Post Deployment Instructions 
## a. Authorize Connections
* Once deployment is complete, you will need to authorize each connection.
  - Click the Teams connection resource
  - Click edit API connection
  - Click Authorize
  - Sign in
  - Click Save
  - Repeat steps for other connections such as Office 365 connection and Wildfire API Connection (For authorizing the Wildfire API connection, API Key needs to be provided)
* In Logic App designer authorize Teams channel connection as well, for playbooks posting adaptive cards.

## b. Configurations in Sentinel
- In Azure sentinel analytical rules should be configured to trigger an incident with filehash and URL. 
- Configure the automation rules to trigger the playbook.

<a name="references">

# References

 Connector
* [Wildfire Connector](Connectors/WildFireConnector/readme.md)

Playbooks
* [WildFire Filehash Enrichment](/Playbooks/FileHash-Enrichment/readme.md)
* [WildFire Block URL](/Playbooks/Block-URL/readme.md)
* [WildFire Block URL From Teams](/Playbooks/Block-URL-From-Teams/readme.md)


<a name="limitations">

# Known Issues and Limitations
 - We need to authorize the connections after deploying the playbooks.
 - Palo Alto Wildfire API returns response body in XML format. To handle this, 'Parse Json' action is needed to convert xml body into json object.[Refer here](./XMLResponse.xml)