# CheckPhish by Bolster Logic Apps connector and playbook templates

<br>
<img src="https://www.okta.com/sites/default/files/Okta_Logo_BrightBlue_Medium-thumbnail.png" width = 200>
<br>

## Table of Contents

1. [Overview](#overview)
1. [Deploy Custom Connector + 1 Playbook templates](#deployall)
1. [Authentication](#importantnotes)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)
1. [Components of this integration](#components)


<a name="overview">

# Overview

CheckPhish is a real-time URL and website scanner. Once a URL is submitted, CheckPhish engine spins up an automated headless browser to capture a live screenshot, natural language content on the webpage, DOM, WHOIS, and other essential information.

The engine sends this information to multiple deep learning models in the backend that can recognize essential signals like brand logos, sign-in forms, and intent. CheckPhish engine then combines these signals with proprietary threat intel data to identify phishing and scam pages.

## Deploy Custom Connector + 3 Playbook templates
This package includes:
* Custom connector for "CheckPhish by Bolster"
* One playbook template leverage "CheckPhish by Bolster" custom connector

You can choose to deploy the whole package : connector + all three playbook templates, or each one seperately from it's specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FOkta%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FOkta%2Fazuredeploy.json)



# CheckPhish by Bolster connector documentation 

<a name="authentication">

## Authentication
Authentication methods this connector supports- [API Key authentication](https://checkphish.ai/docs/checkphish-api/)

<a name="prerequisites">

### Prerequisites for using and deploying Custom Connector
1. CheckPhish API service end point should be known (ex : https://developers.checkphish.ai)
2. Get an API key.Refer this link [ how to get the API Key](https://checkphish.ai/apiscan/)


<a name="deployment">

### Deployment instructions 
1. Deploy the Custom Connector and playbooks by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required parameteres:

#### a. For custom connector :

* Custom Connector name : Enter the Custom connector name (ex:CheckPhish by Bolster connector)

* Service Endpoint : Enter the okta service end point (ex:https://developers.checkphish.ai)
    
#### b. For CheckPhish-EnrichIncident-URLScanResults playbook :

* Enrich Incident Playbook Name : Enter the playbook name here (Ex:CheckPhish-EnrichIncident-URLScanResults)
    
 

<a name="postdeployment">

### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Azure Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for other connections such as Teams connection and Okta Api  Connection (For authorizing the Okta API connection, API Key needs to be provided)
#### b. Configurations in Sentinel
1. In Azure sentinel analytical rules should be configured to trigger an incident with risky user account 
2. Configure the automation rules to trigger the playbooks


<a name="components">

##  Components of this integration

 Connector
* [OktaCustomConnector](https://github.com/Azure/Azure-Sentinel/master/Playbooks/Okta/OktaCustomConnector)

Playbooks
* [Okta-Response From Teams : Playbook to perform different actions on user on Okta and add user deatils to incident](https://github.com/Azure/Azure-Sentinel/master/Playbooks/Okta/OktaPlaybooks/Okta-EnrichIncidentWithUserDetails)
* [Okta-Enrich incident with user details : Playbook to enrich incident with user deatils and user groupdetails ](https://github.com/Azure/Azure-Sentinel/master/Playbooks/Okta/OktaPlaybooks/Okta-EnrichIncidentWithUserDetails)
* [Okta-PromptUser : Playbook to prompt risky user about the malicious activity](https://github.com/Azure/Azure-Sentinel/master/Playbooks/Okta/OktaPlaybooks/Okta-PromptUser)



