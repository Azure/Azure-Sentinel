# Okta Logic Apps connector and playbook templates

<br>
<img src="https://www.okta.com/sites/default/files/Okta_Logo_BrightBlue_Medium-thumbnail.png" width = 200>
<br>

## Table of Contents

1. [Overview](#overview)
1. [Deploy Custom Connector + 3 Playbook templates](#deployall)
1. [Authentication](#importantnotes)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)
1. [Components of this integration](#components)


<a name="overview">

# Overview

Okta is an enterprise-grade, identity management service, built for the cloud, but compatible with many on-premises applications. 
With Okta, IT can manage any employee's access to any application or device. Okta runs in the cloud, on a secure, reliable, extensively audited platform, which integrates deeply with on-premises applications, directories, and identity management systems.

## Deploy Custom Connector + 3 Playbook templates
This package includes:
* Custom connector for Okta
* Three playbook templates leverage Okta custom connector

You can choose to deploy the whole package : connector + all three playbook templates, or each one seperately from it's specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FOkta%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FOkta%2Fazuredeploy.json)



# Okta connector documentation 

<a name="authentication">

## Authentication
Authentication methods this connector supports- [API Key authentication](https://developer.okta.com/docs/reference/api/authn/)

<a name="prerequisites">

### Prerequisites for using and deploying Custom Connector
1. Okta service end point should be known (ex : https://{yourOktaDomain}/)
2. Generate an API key.Refer this link [ how to generate the API Key](https://developer.okta.com/docs/guides/create-an-api-token/overview/)
3. API key needs to have admin previligies to perform specific actions like expire password on okta accounts


<a name="deployment">

### Deployment instructions 
1. Deploy the Custom Connector and playbooks by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required parameteres:

#### a. For custom connector :

* Custom Connector name : Enter the Custom connector name (ex:contoso Okta connector)

* Service Endpoint : Enter the okta service end point (ex:https://{yourOktaDomain})
    
#### b. For Okta-EnrichIncidentWithUserDetails playbook :

* Enrich Incident Playbook Name : Enter the playbook name here (Ex:OktaPlaybook)
    
#### c. For Okta-PromptUser playbook :

* Prompt User Playbook Name : Enter the playbook name here (Ex:OktaPlaybook)

* Teams GroupId : Enter the Teams channel id to send the adaptive card

* Teams ChannelId : Enter the Teams Group id to send the adaptive card
    [Refer the below link to get the channel id and group id](https://docs.microsoft.com/powershell/module/teams/get-teamchannel?view=teams-ps)

#### d. For Okta-ResponseFromTeams playbook :

 * Response From Teams Playbook Name : Enter the playbook name here (Ex:OktaPlaybook)
 

<a name="postdeployment">

### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Microsoft Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for other connections such as Teams connection and Okta Api  Connection (For authorizing the Okta API connection, API Key needs to be provided)
#### b. Configurations in Sentinel
1. In Microsoft sentinel analytical rules should be configured to trigger an incident with risky user account 
2. Configure the automation rules to trigger the playbooks


<a name="components">

##  Components of this integration

 Connector
* [OktaCustomConnector](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/Okta%20Single%20Sign-On/Playbooks/OktaCustomConnector)

Playbooks
* [Okta-Response From Teams : Playbook to perform different actions on user on Okta and add user deatils to incident](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/Okta%20Single%20Sign-On/Playbooks/OktaPlaybooks/Okta-EnrichIncidentWithUserDetails)
* [Okta-Enrich incident with user details : Playbook to enrich incident with user deatils and user groupdetails ](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/Okta%20Single%20Sign-On/Playbooks/OktaPlaybooks/Okta-EnrichIncidentWithUserDetails)
* [Okta-PromptUser : Playbook to prompt risky user about the malicious activity](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/Okta%20Single%20Sign-On/Playbooks/OktaPlaybooks/Okta-PromptUser)



