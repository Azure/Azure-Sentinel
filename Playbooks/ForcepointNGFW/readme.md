  #Forcepoint NGFW Logic Apps Custom Connectors and playbook templates

  ![forcepoint](./Playbooks/logo.jpg)


## Table of Contents

1. [Overview](#overview)
1. [Deploy 2 Custom Connectors + 6 Playbook templates](#deployall)
1. [Authentication](#importantnotes)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)
1. [References](#references)
1. [Limitations](#limitations)


<a name="overview">

# Overview

Forcepoint Next Generation Firewall (NGFW) connects and protects people and the data they use throughout the enterprise network – all with the greatest efficiency, availability and security.

<a name="deploy">

# Deploy 2 Custom Connectors + 6 Playbook templates
This package includes:
* Two Custom connectors for ForcepointNGFW.
* Six playbook templates leverage ForcepointNGFW custom connectors.

You can choose to deploy the whole package : two connectors + all six playbook templates, or each one seperately from it's specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FForcepointNGFW%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FForcepointNGFW%2Fazuredeploy.json)


# ForcepointNGFW documentation 

<a name="authentication">

# Authentication
No Authentication

<a name="prerequisites">

# Prerequisites for using and deploying 2 Custom Connectors + 6 playbooks
1. Forcepoint SMC API Key should be known.[Refer here](http://www.websense.com/content/support/library/ngfw/v610/rfrnce/ngfw_6100_ug_smc-api_a_en-us.pdf )
2. Forcepoint SMC Version number should be known. [Refer here](https://help.stonesoft.com/onlinehelp/StoneGate/SMC/)
3. Forcepoint SMC service endpoint should be known. (e.g.  Https://{forcepointdomain:PortNumber/})
4. Forcepoint FUID service endpoint should be known. (e.g.  https://{forcepointdomain:PortNumber/})
5. IP address list name for blocking IP address present in SMC should be known.
6. URL list name for blocking URLs present in SMC should be known.
7. Users must have access to Microsoft Teams and they should be a part of a Teams channel and also Power Automate app should be installed in the Microsoft Teams channel.


<a name="deployment">

# Deployment instructions 
1. Deploy the Custom Connectors and playbooks by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters for deploying custom connector and playbooks

| Parameter  | Description |
| ------------- | ------------- |
|**For Playbooks**|                 |
| **Block IP Response On Teams PlaybookName** | Enter the Block IP Response On Teams Playbook Name here without spaces. |
| **Block IP By Username PlaybookName** | Enter the Block IP By Username Playbook Name here without spaces. |
| **Block IP PlaybookName**|Enter the Block IP Playbook Name here without spaces.|
|**Block URL PlaybookName**|Enter the Block URL Playbook Name here without spaces.|
|**Enrichment IP PlaybookName**|Enter the Enrichment IP Playbook Name here without spaces.|
|**Enrichment URL PlaybookName**|Enter the Enrichment URL Playbook Name here without spaces.|
| **Forcepoint SMC Api Key**  | Enter the SMC API Key. | 
| **SMC Version Number** | Enter the version number of SMC. |
|**IP List Name**|Enter IP List Name.|
|**URL List Name**|Enter URL List Name.|
|**For Custom Connectors**|                             |
|**Service EndPoint FUID Connector**|Enter the Forcepoint FUID Service End Point.|
| **SMC Connector name**|Enter the name of your Forcepoint SMC Connector without spaces.|
|**Service EndPoint SMC Connector**|Enter the Forcepoint SMC Service End Point.|

<a name="postdeployment">

# Post-Deployment Instructions 
## a. Authorize API connections
* Once deployment is complete, go under deployment details and authorize teams connection. 
1.  Click the Teams connection resource
2.  Click **Edit API connection**
3.  Click Authorize
4.  Sign in
5.  Click Save

* In Logic App designer, go to "Post an adaptive card to teams channel" action and select your Teams name and Channel name from the dropdown.
*  In In Logic App designer again, go to "Post adaptive card in a chat or channel" action and select your Teams name, Channel name, and "Flow bot" for "Post as" parameter from the dropdown. 

## b. Configurations in Sentinel
1. In Azure sentinel analytical rules should be configured to trigger an incident with risky IP address or URL. 
2. Configure the automation rules to trigger the playbooks.


<a name="references">

#  Reference to the playbook templates and the connectors

 Connector
* [Forcepoint SMC Connector](/Connector/ForcepointSMCApiConnector/readme.md)


Playbooks
* [ResponseOnTeamsBlockIP-ForcepointNGFW](/Playbooks/ResponseOnTeamsBlockIP-ForcepointNGFW/readme.md)
* [BlockIPbyUsername-ForcepointNGFW](/Playbooks/BlockIPbyUsername-ForcepointNGFW/readme.md)
* [BlockIP-ForcepointNGFW](/Playbooks/BlockIP-ForcepointNGFW/readme.md)
* [BlockURL-ForcepointNGFW](/Playbooks/BlockURL-ForcepointNGFW/readme.md)
* [Enrichment-IP-ForcepointNGFW](/Playbooks/Enrichment-IP-ForcepointNGFW/readme.md)
* [Enrichment-URL-ForcepointNGFW](/Playbooks/Enrichment-URL-ForcepointNGFW/readme.md)

<a name="limitations">

# Known Issues and Limitations
* We need to authorize the teams connection after deploying the playbooks.



