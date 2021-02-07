  # PAN-OS Logic Apps connector and playbook templates

  <img src="./PaloAltoCustomConnector/PAN-OS_CustomConnector.png" alt="drawing" width="20%"/>

## Table of Contents

1. [Overview](#overview)
1. [Deploy Custom Connector + 3 Playbook templates](#deployall)
1. [Authentication](#authentication)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)



<a name="overview">

# Overview

PAN‑OS is the software that runs all Palo Alto Networks next-generation firewalls. By leveraging the key technologies that are built into PAN‑OS natively—App‑ID, Content‑ID, Device-ID, and User‑ID—you can have complete visibility and control of the applications in use across all users and devices in all locations all the time. And, because inline ML and the application and threat signatures automatically reprogram your firewall with the latest intelligence, you can be assured that all traffic you allow is free of known and unknown threats.

## Deploy Custom Connector + 3 Playbook templates
This package includes:
* Custom connector for PAN-OS.
* Three playbook templates leverage PAN-OS custom connector.

You can choose to deploy the whole package : connector + all three playbook templates, or each one seperately from it's specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fdev.azure.com/SentinelAccenture/_git/Sentinel-Accenture%20Logic%20Apps%20connectors?version=GBPaloAlto-PAN-OS&path=%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://login.microsoftonline.us/organizations/oauth2/v2.0/authorize?client_id=c836cbdb-7a5b-44cc-a54f-564b4b486fc6&response_type=code%20id_token&scope=https%3A%2F%2Fmanagement.core.usgovcloudapi.net%2F%2Fuser_impersonation%20openid%20email%20profile&state=OpenIdConnect.AuthenticationProperties%3DaURMJdv8OOjkos8hJrPp2UR3SiCuzPqKSCojZXlvmudMu2wCQivYUBL-PUpm2VklFejdDnBr9Us32MzfuH8tith-XldC_OIlCqCjwB950H9ELHA76IfBBh19cTzh9-nsHhkQkk8wQDSE6bot7rUuEQB8IDVJgDMCfv1HYuUg9brFyPen2T4DF7f3SxN7Wwxfj87B5iDMqyoU1AHKentIKfwHsDQCVmhbtWdvSgPbWWABKGY-a7b1vkmjWNmo8x5v&response_mode=form_post&nonce=637443070124899368.YjM5MDcwYzMtODJkZC00MzRmLTgxNDctMjhhZjY0MWRmNjcxZGRiOWNmMmItMDAyNS00MTIxLWE4MDUtMjdiOTE4MWJhMjg0&redirect_uri=https%3A%2F%2Fportal.azure.us%2Fsignin%2Findex%2F&site_id=501430&msafed=0&client-request-id=5cc07576-a6f1-4a94-b26f-830ed1c4ad77&x-client-SKU=ID_NET45&x-client-ver=5.3.0.0)


# PAN-OS connector documentation 

<a name="authentication">

## Authentication
Authentication methods this connector supports- [API Key authentication](https://paloaltolactest.trafficmanager.net/restapi-doc/#tag/key-generation)

<a name="prerequisites">

### Prerequisites for using and deploying Custom Connector
1. PAN-OS service end point should be known. (e.g. https://{paloaltodomain})
2. Generate an API key. [Refer this link on how to generate the API Key](https://paloaltolactest.trafficmanager.net/restapi-doc/#tag/key-generation)
3. Address group should be created for PAN-OS for blocking/unblocking address objects and this address group should be used while creating playbooks.


<a name="deployment">

### Deployment instructions 
1. Deploy the Custom Connector and playbooks by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters for deploying custom connector and playbooks

| Parameters | Description |
|----------------|--------------|
|**Custom connector :**| **Custom Connector name :** Enter the Custom connector name (e.g. contoso PAN-OS connector)<br> **Service Endpoint :** Enter the PAN-OS service end point (e.g. https://{yourPaloAltoDomain})|
|**PaloAlto-PAN-OS-GetURLCategoryInfo playbook :**| **Enrich Incident Playbook Name :** Enter the playbook name here (e.g. PAN-OSPlaybook)|
|**PaloAlto-PAN-OS-BlockIP playbook :**|**PaloAlto-PAN-OS-BlockIP Playbook Name:** Enter the playbook name here (e.g. PAN-OS Playbook)<br> **Teams GroupId:** Enter the Teams channel id to send the adaptive card<br> **Teams ChannelId:** Enter the Teams Group id to send the adaptive card <br>[Refer the below link to get the channel id and group id](https://docs.microsoft.com/en-us/powershell/module/teams/get-teamchannel?view=teams-ps)<br> **Predefined address group name:** Enter the pre-defined address group name which blocks IP
|**PaloAlto-PAN-OS-BlockURL playbook :**|**PaloAlto-PAN-OS-BlockURL Playbook Name :** Enter the playbook name here (e.g. PAN-OS Playbook)<br> **Teams GroupId :** Enter the Teams channel id to send the adaptive card<br> **Teams ChannelId :** Enter the Teams Group id to send the adaptive card <br> [Refer the below link to get the channel id and group id](https://docs.microsoft.com/en-us/powershell/module/teams/get-teamchannel?view=teams-ps)<br> **Predefined address group name :** Enter the pre-defined address group name which blocks URL

<a name="postdeployment">

### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Azure Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for other connections such as Teams connection and PAN-OS API  Connection (For authorizing the PAN-OS API connection, API Key needs to be provided)
#### b. Configurations in Sentinel
1. In Azure sentinel analytical rules should be configured to trigger an incident with risky user account. 
2. Configure the automation rules to trigger the playbooks.
