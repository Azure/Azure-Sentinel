# Okta Logic Apps connector and playbook templates


## Table of Contents

1. [Overview](#overview)
1. [Deploy Custom Connector + 3 Playbook templates](#deployall)
1. [Authentication](#importantnotes)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)
1. [References](#references)


<a name="overview">

# Overview

Okta is an enterprise-grade, identity management service, built for the cloud, but compatible with many on-premises applications. 
With Okta, IT can manage any employee's access to any application or device. Okta runs in the cloud, on a secure, reliable, extensively audited platform, which integrates deeply with on-premises applications, directories, and identity management systems.

## Deploy Custom Connector + 3 Playbook templates
This package includes:
* Custom connector for Okta
* Three playbook templates leverage Okta custom connector

You can choose to deploy the whole package : connector + all three playbook templates, or each one seperately from it's specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fdev.azure.com/SentinelAccenture/_git/Sentinel-Accenture%20Logic%20Apps%20connectors?version=GBOkta&path=%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://login.microsoftonline.us/organizations/oauth2/v2.0/authorize?client_id=c836cbdb-7a5b-44cc-a54f-564b4b486fc6&response_type=code%20id_token&scope=https%3A%2F%2Fmanagement.core.usgovcloudapi.net%2F%2Fuser_impersonation%20openid%20email%20profile&state=OpenIdConnect.AuthenticationProperties%3DaURMJdv8OOjkos8hJrPp2UR3SiCuzPqKSCojZXlvmudMu2wCQivYUBL-PUpm2VklFejdDnBr9Us32MzfuH8tith-XldC_OIlCqCjwB950H9ELHA76IfBBh19cTzh9-nsHhkQkk8wQDSE6bot7rUuEQB8IDVJgDMCfv1HYuUg9brFyPen2T4DF7f3SxN7Wwxfj87B5iDMqyoU1AHKentIKfwHsDQCVmhbtWdvSgPbWWABKGY-a7b1vkmjWNmo8x5v&response_mode=form_post&nonce=637443070124899368.YjM5MDcwYzMtODJkZC00MzRmLTgxNDctMjhhZjY0MWRmNjcxZGRiOWNmMmItMDAyNS00MTIxLWE4MDUtMjdiOTE4MWJhMjg0&redirect_uri=https%3A%2F%2Fportal.azure.us%2Fsignin%2Findex%2F&site_id=501430&msafed=0&client-request-id=5cc07576-a6f1-4a94-b26f-830ed1c4ad77&x-client-SKU=ID_NET45&x-client-ver=5.3.0.0)


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
    [Refer the below link to get the channel id and group id](https://docs.microsoft.com/en-us/powershell/module/teams/get-teamchannel?view=teams-ps)

#### d. For Okta-ResponseFromTeams playbook :

 * Response From Teams Playbook Name : Enter the playbook name here (Ex:OktaPlaybook)
 

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


<a name="references">

##  Reference to the playbook templates and the connector

 Connector
* [OktaCustomConnector](https://dev.azure.com/SentinelAccenture/_git/Sentinel-Accenture%20Logic%20Apps%20connectors?path=%2FOktaCustomConnector%2Fazuredeploy)

Playbooks
* [Okta-Response From Teams : Playbook to perform different actions on user on Okta and add user deatils to incident](https://dev.azure.com/SentinelAccenture/_git/Sentinel-Accenture%20Logic%20Apps%20connectors?path=%2FOktaPlaybooks%2FOkta-ResponseFromTeams%2Fazuredeploy.json)
* [Okta-Enrich incident with user details : Playbook to enrich incident with user deatils and user groupdetails ](https://dev.azure.com/SentinelAccenture/_git/Sentinel-Accenture%20Logic%20Apps%20connectors?path=%2FOktaPlaybooks%2FOkta-EnrichIncidentWithUserDetails%2Fazuredeploy.json)
* [Okta-PromptUser : Playbook to prompt risky user about the malicious activity](https://dev.azure.com/SentinelAccenture/_git/Sentinel-Accenture%20Logic%20Apps%20connectors?path=%2FOktaPlaybooks%2FOkta-PromptUser%2Fazuredeploy.json)



