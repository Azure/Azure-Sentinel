# Cisco ISE Logic Apps connector and playbook templates

<img src="./cisco-logo.png" alt="drawing" width="20%"/><br>

## Table of Contents

1. [Overview](#overview)
1. [Custom Connector + 3 Playbook templates deployment](#deployall)
1. [Authentication](#importantnotes)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post-Deployment Steps](#postdeployment)
1. [References](#references)
1. [Known issues and limitations](#limitations)

<a name="overview">

# Overview

Cisco Identity Services Engine (ISE) is a security policy management platform that provides secure access to network resources.

<a name="deployall">

## Custom Connectors + 3 Playbook templates deployment

This package includes:

* [Logic Apps custom connector for Cisco ISE ERS API](./CiscoISEConnector)

* These three playbook templates leverage Cisco ISE custom connector:
  * [Response – release rejected endpoints](./Playbooks/CiscoISE-FalsePositivesClearPolicies) - releases rejected endpoints that are in safe list.
  * [Response - suspend guest user](./Playbooks/CiscoISE-SuspendGuestUser) - suspends guest user.
  * [Response - assign policy to an endpoint](./Playbooks/CiscoISE-TakeEndpointActionFromTeams) - posts adaptive card to Teams channel and assigns policy to an endpoint after approving in Teams.

You can choose to deploy the whole package: connectors + all three playbook templates, or each one seperately from its specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCisco%2520ISE%2FPlaybooks%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCisco%2520ISE%2FPlaybooks%2Fazuredeploy.json)

# Cisco ISE connector documentation 

<a name="authentication">

## Authentication

This connector supports Basic authentication. When creating the connection for the custom connector, you will be asked to provide user and password which you generated in Cisco ISE admin UI.

<a name="prerequisites">

### Prerequisites in Cisco ISE

To get Cisco ISE ERS API credentials [follow the instructions](https://developer.cisco.com/docs/identity-services-engine/#!setting-up).

Cisco ISE connector uses [On-Premises Data Gateway](https://docs.microsoft.com/data-integration/gateway/service-gateway-onprem). Therefore [installation of the On-Premises Data Gateway](https://docs.microsoft.com/azure/logic-apps/logic-apps-gateway-install) and [creation of the On-Premises Data Gateway resource](https://docs.microsoft.com/azure/logic-apps/logic-apps-gateway-connection#create-azure-gateway-resource) are required.


<a name="deployment">

### Deployment instructions

1. To deploy Custom Connectors and Playbooks, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters for deploying Custom Connectors and Playbooks

| Parameters | Description |
|----------------|--------------|
|**For Connector**|
|**API Hostname** | Hostname of the Cisco ISE instance.|
|**API Port** | Port number of Cisco ISE ERS API. By default 9060.|
|**For Playbooks**|
|**CiscoISE-FalsePositivesClearPolicies Playbook Name** | Enter the playbook name here (e.g. CiscoISE-FalsePositivesClearPolicies)|
|**CiscoISE-SuspendGuestUser Playbook Name** | Enter the playbook name here (e.g. CiscoISE-SuspendGuestUser)|
|**CiscoISE-TakeEndpointActionFromTeams Playbook Name** | Enter the playbook name here (e.g. CiscoISE-TakeEndpointActionFromTeams)|
|**WatchlistName** | Value of WatchlistName parameter in CiscoISE-FalsePositivesClearPolicies playbook. Name of the Watchlist that contains safe MAC addresses list|
|**WatchlistFieldName** | Value of WatchlistFieldName parameter in CiscoISE-FalsePositivesClearPolicies playbook. Watchlist field name that contains MAC address|
|**TeamsGroupId** | Value of TeamsGroupId parameter in CiscoISE-TakeEndpointActionFromTeams playbook. Id of the Teams Group where the adaptive card will be posted.|
|**TeamsChannelId** | Value of TeamsChannelId parameter in CiscoISE-TakeEndpointActionFromTeams playbook. Id of the Teams Channel where the adaptive card will be posted.|
|**PolicyName** | Value of PolicyName parameter in CiscoISE-TakeEndpointActionFromTeams playbook. Policy name to be assigned to an identity.|

<br>
<a name="postdeployment">

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Click the Azure Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections

#### b. Configurations in Sentinel

Each Playbook requires a different type of configuration. Check documentation for each Playbook.

<a name="limitations">

## Known Issues and Limitations