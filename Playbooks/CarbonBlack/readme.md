  # Carbon Black Logic Apps connector and playbook templates

  <img src="./CarbonBlackConnector/CarbonBlack.PNG" alt="drawing" width="20%"/><br>


## Table of Contents

1. [Overview](#overview)
1. [Deploy Custom Connector + 3 Playbook templates](#deployall)
1. [Authentication](#importantnotes)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)
1. [References](#references)
1. [Known issues and limitations](#limitations)


<a name="overview">

# Overview

The Carbon Black Cloud is a cloud-native endpoint protection platform (EPP) that provides what you need to secure your endpoints using a single, lightweight agent and an easy-to-use console.

<a name="deployall">

## Deploy Custom Connector + 3 Playbook templates
This package includes:
* Logic Apps custom connector for Carbon Black
* Three playbook templates leverage CarbonBlack custom connector.

You can choose to deploy the whole package: connector + all three playbook templates, or each one seperately from it's specific folder.


[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2FSOAR-connectors-Private-Preview%2FPlaybooks%2FCarbonBlack%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2FSOAR-connectors-Private-Preview%2FPlaybooks%2FCarbonBlack%2Fazuredeploy.json)



# CarbonBlack connector documentation 

<a name="authentication">

## Authentication
This connector supports API Key authentication. When creating the connection for the custom connector, you will be asked to provide the API key which you generated in Carbon Black platform. [API Key authentication](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key).

<a name="prerequisites">

### Prerequisites for using and deploying Custom Connector
1. CarbonBlack clound end point should be known. (e.g.  https://{CarbonblackBaseURL})
2. Generate an API key ([learn how](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key)), and grant it the following access levels:
    * 1
    * 2
    * 3


<a name="deployment">

### Deployment instructions 
1. Deploy the Custom Connector and playbooks by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters for deploying custom connector and playbooks

| Parameters | Description |
|----------------|--------------|
|**For Custom Connector**|
|**Custom Connector name**| Enter the Custom connector name (e.g. CarbonBlackConnector)|
|**Service Endpoint** | Enter the CarbonBlack clound end point (e.g. https://{CarbonblackBaseURL})|
|**For Playbooks**|
|**CarbonBlack-TakeDeviceActionFromTeams Playbook Name**|  Enter the playbook name here (e.g. CarbonBlack-TakeDeviceActionFromTeams)|
|**CarbonBlack-DeviceEnrichment Playbook Name** |Enter the playbook name here (e.g. CarbonBlack-QuarantineDevice)|
|**CarbonBlack-QuarantineDevice Playbook Name** | Enter the playbook name here (e.g. CarbonBlack-DeviceEnrichment)| 
|**OrganizationId** | Enter the OrganizationId|
|**PolicyId** | Enter the pre-defined PolicyId|
|**Teams GroupId** | Enter the Teams channel id to send the adaptive card|
|**Teams ChannelId** | Enter the Teams Group id to send the adaptive card [Refer the below link to get the channel id and group id](https://docs.microsoft.com/en-us/powershell/module/teams/get-teamchannel?view=teams-ps)|

<br>
<a name="postdeployment">

### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Azure Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for other connections such as Teams connection and CarbonBlack connector API  Connection (For authorizing the CarbonBlack connector API connection, API Key needs to be provided. The API Key is the combination of API Key / API Id)
#### b. Configurations in Sentinel
1. In Azure sentinel analytical rules should be configured to trigger an incident with risky user account. 
2. Configure the automation rules to trigger the playbooks.


<a name="limitations">

## Known Issues and Limitations
1. Quaraninte is not support for Linux OS devices.
