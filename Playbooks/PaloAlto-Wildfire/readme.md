  # PaloAlto WildFire Logic Apps Custom Connector and Playbook templates

![wildfire](./wildfirelogo.png)

## Table of Contents

1. [Overview](#overview)
1. [Prerequisites](#prerequisites)
1. [Authentication](#authentication)
1. [Deploy PaloAlto PAN-OS custom connector](#deplyoment) 
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
- PaloAlto Pan-OS Custom Connector needs to be deployed prior to the deployment of playbooks under the same subscription as well as same resource group and capture the name of the connector during the deployment.
- Wildfire API end point should be known. ([WildFire Console](https://wildfire.paloaltonetworks.com))
- Wildfire API key should be known. ([Generate WildFire API Key](https://wildfire.paloaltonetworks.com/wildfire/dashboard)).
- Create the security policy rule on PAN-OS VM and capture rule name.
- Posting a message or adaptive card as the Flow bot to a channel requires that the Power Automate should be set to "allow" state in Teams admin center.

<a name="authentication">

# Authentication
WildFire Custom Connector supports: API Key Authentication 


<a name="deplyoment">

# Deploy PaloAlto PAN-OS custom connector 

To deploy PaloAlto PAN-OS Custom connector goto [Pre-requisites to deploy PaloAlto PAN-OS Custom Connector](/Connectors/PaloAltoConnector/readme.md)

Click on the below button to deploy PaloAlto PAN-OS Custom Connector in your Azure subscription.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FPaloAlto-Wildfire%2FConnectores%2FPaloAltoConnector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FPaloAlto-Wildfire%2FConnectores%2FPaloAltoConnector%2Fazuredeploy.json)


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
| **Filehash Enrichment Playbook Name**  | Enter the Filehash Enrichment Playbook Name (e.g. Wildfire_filehash_enrichment)  |
| **URL Verdict Playbook Name** | Enter the URL verdict Playbook Name (e.g. Wildfire_URL_verdict) |
| **URL Verdict On Teams Playbook Name** | Enter the URL verdict on teams Playbook Name  (e.g. URL_verdict_on_teams) |
| **Wildfire Custom Connector Name** | Enter the name of WildFire custom connector |
| **Wildfire Service End Point** | Enter the Service End Point of Wildfire API [WildFire Console](https://wildfire.paloaltonetworks.com)|
| **Wildfire API Key**  | Enter the WildFire API Key| 
| **Notification Email** | Enter the DL or SOC email address for receiving filehash report|
| **Palo Alto Custom Connector Name**  | Enter the PaloAlto PAN-OS custom connector name  |
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
* [Wildfire_Filehash_Enrichment](/Playbooks/Wildfire_Filehash_Enrichment/readme.md)
* [Wildfire_URL_Verdict_Automation](/Playbooks/Wildfire_URL_Verdict_Automation/readme.md)
* [Wildifre_URL_verdict_on_Teams](/Playbooks/Wildfire_URL_Verdict_on_Teams/readme.md)


<a name="limitations">

# Known Issues and Limitations
 - We need to authorize the connections after deploying the playbooks.