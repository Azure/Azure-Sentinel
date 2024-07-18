 # Fortinet Logic Apps connector, Function app and playbook templates


![Fortinet](./Fortinetlogo.png)<br>


## Table of Contents

1. [Overview](#overview)
1. [Deploy Custom Connector + Function App + 3 Playbook templates](#deployall)
1. [Authentication](#authentication)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)
1. [Limitations](#limitations)


<a name="overview">

# Overview

FortiGate, a next-generation firewall from IT Cyber Security leaders Fortinet, provides the ultimate threat protection for businesses of all sizes. This integration is built over the FortiOS REST API which allows you to perform configuration and monitoring operations on a FortiGate appliance or VM. 

<a name="deployall">

## Deploy Custom Connector + Function App + 3 Playbook templates
This package includes:
* [Custom connector](./FortinetCustomConnector) 
* [Function App](./FortinetFortigateFunctionApp) 
* Three playbook templates leverage fortinet custom connector and Function App:
  * [Block IP](./Fortinet_ResponseOnIP)
  * [Block URL](./Fortinet_ResponseOnURL)
  * [Enrich incident](./Fortinet_IncidentEnrichment)
  
*The Azure Function handles the Get calls on FortiOS API in the playbook templates. These calls are not part of the custom connector due to platform limitations.*


You can choose to deploy the whole package: connector + Function App + all three playbook templates, or each one seperately from it's specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FFortinet-FortiGate%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FFortinet-FortiGate%2Fazuredeploy.json)

# Fortinet connector documentation 

<a name="authentication">

## Authentication
Authentication methods this connector supports- [API Key authentication](https://www.insoftservices.uk/FortiGate-rest-api-token-authentication)

<a name="prerequisites">

### Prerequisites for using and deploying Custom Connector

- Function app must deploy before deploying consloidated template 
- Fortinet end point should be known. [Fortinet Console](https://{https://fndn.fortinet.net/index.php?/category/1-fortianswers/})
- Generate an API key ([learn how](https://www.insoftservices.uk/fortigate-rest-api-token-authentication)).
- Create the key vaults and capture secret identifier
- Create the managed identity and capture name [Create user assigned manage identity](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/how-to-manage-ua-identity-portal)
<a name="deployment">
 
### Deployment instructions 
- Deploy the Custom Connector and playbooks by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
- Fill in the required parameters for deploying custom connector and playbooks

#### Parameters

| Parameter  | Description |
| ------------- | ------------- |
| **Endpoint URL**  | Enter the Fortinet end point (e.g. https://{FortnetTrafficManager})  |
| **Secret identifier** | Enter the Secret identifier which is captured in key vaults secret |
| **Fortinet-ResponseOnIP Playbook Name** | Enter the playbook name here for ResponseOnIP playbook (e.g. Fortinet-ResponseOnIP) |
| **Fortinet-ResponseOnUrl Playbook Name** | Enter the playbook name here for ResponseOnURL (e.g. Fortinet-ResponseOnUrl) |
| **Fortinet-Enrichment Playbook Name**  | Enter the playbook name here for Enrichment (e.g. Fortinet-Enrichment) | 
| **Teams GroupId** | Enter the Teams channel id to send the adaptive card |
| **Teams ChannelId**  | Enter the Teams Group id to send the adaptive card [Refer the below link to get the channel id and group id](https://docs.microsoft.com/powershell/module/teams/get-teamchannel?view=teams-ps)|
| **Function app name** | Enter the Function app name which you created as prerequisites|
| **User identifier name** | Enter the User identifier name which you created for the Managed Identity [Create user assigned manage identity](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/how-to-manage-ua-identity-portal) |

<a name="postdeployment">

### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
- Click the Microsoft Sentinel connection resource
- Click edit API connection
- Click Authorize
- Sign in
- Click Save
- Repeat steps for other connections such as Teams connection and Fortinet connector API Connection (For authorizing the fortinet connector API connection, API Key needs to be provided.) and API virustotal connection (URL:https://www.virustotal.com/gui/)
- Open each playbook go to logic app designer-->click on each function call action in the logic app and go to "Managed identity" dropdown and select user identity and save playbook.
- Go to sentinel hook playbook to Microsoft Sentinel rules.
#### b. Configurations in Sentinel
- In Microsoft Sentinel analytical rules should be configured to trigger an incident with risky user account. 
- Configure the automation rules to trigger the playbooks.


<a name="limitations">

## Known Issues and Limitations

- When pre-defined group reaches the max limit user must create the new pre-defined group and change in the playbook
