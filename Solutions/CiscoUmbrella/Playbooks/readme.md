# Cisco Umbrella Logic Apps connector and playbook templates

<img src="./cisco-logo.png" alt="drawing" width="20%"/><br>

## Table of Contents

1. [Overview](#overview)
1. [Custom Connectors + 4 Playbook templates deployment](#deployall)
1. [Authentication](#importantnotes)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post-Deployment Steps](#postdeployment)
1. [References](#references)
1. [Known issues and limitations](#limitations)

<a name="overview">

# Overview

Cisco Umbrella is a Cloud driven Secure Internet Gateway that provides protection from Internet based threats, for users wherever they go.

<a name="deployall">

## Custom Connectors + 4 Playbook templates deployment

This package includes:

* [Logic Apps custom connector for Cisco Umbrella Enforcement API](./CiscoUmbrellaEnforcementAPIConnector)
* [Logic Apps custom connector for Cisco Umbrella Investigate API](./CiscoUmbrellaInvestigateAPIConnector)
* [Logic Apps custom connector for Cisco Umbrella Management API](./CiscoUmbrellaManagementAPIConnector)
* [Logic Apps custom connector for Cisco Umbrella Network Device Management API](./CiscoUmbrellaNetworkDeviceManagementAPIConnector)

* These three playbook templates leverage Cisco Umbrella custom connectors:
  * [Response – assign policy to identity](./Playbooks/CiscoUmbrella-AssignPolicyToIdentity) - assigns a new DNS or a web policy (provided on the playbook deplyment step) to an identity.
  * [Response - block domain](./Playbooks/CiscoUmbrella-BlockDomain) - add domains to a customer's domain lists.
  * [Enrichment - add security info about domain to incident](./Playbooks/CiscoUmbrella-GetDomainInfo) - collects security information about domains and post it as an incident comment.
  * [Response - add IP to destination list](./Playbooks/CiscoUmbrella-AddIpToDestinationList) - sends an adaptive card to the Teams channel where the analyst can select the destionation list to add IP to.

You can choose to deploy the whole package: connectors + all three playbook templates, or each one seperately from its specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCiscoUmbrella%2FPlaybooks%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCiscoUmbrella%2FPlaybooks%2Fazuredeploy.json)

# Cisco Umbrella connectors documentation 

<a name="authentication">

## Authentication

Each Logic Apps Custom Connector uses different type of authentication. Check documentation for each connector.

<a name="prerequisites">

### Prerequisites in Cisco Umbrella

Each Logic Apps Custom Connector requires different type of credentials. Check documentation for each connector.

<a name="deployment">

### Deployment instructions 

1. To deploy Custom Connectors and Playbooks, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters for deploying Custom Connectors and Playbooks

| Parameters | Description |
|----------------|--------------|
|**For Playbooks**|
|**CiscoUmbrella-AssignPolicyToIdentity Playbook Name** | Enter the playbook name here (e.g. CiscoUmbrella-AssignPolicyToIdentity)|
|**CiscoUmbrella-BlockDomain Playbook Name** | Enter the playbook name here (e.g. CiscoUmbrella-BlockDomain)|
|**CiscoUmbrella-GetDomainInfo Playbook Name** | Enter the playbook name here (e.g. CiscoUmbrella-GetDomainInfo)|
|**CiscoUmbrella-AddIpToDestinationList_Playbook_Name** | Enter the playbook name here (e.g. CiscoUmbrella-AddIpToDestinationList)|
|**PolicyId** | ID of the DNS or web policy to use in CiscoUmbrella-AssignPolicyToIdentity playbook|
|**CiscoUmbrellaOrganizationId** | Organization id in Cisco Umbrella for CiscoUmbrella-AddIpToDestinationList playbook|
|**TeamsGroupId** | Id of the Teams Group where the adaptive card will be posted for CiscoUmbrella-AddIpToDestinationList playbook|
|**TeamsChannelId** | Id of the Teams Channel where the adaptive card will be posted for CiscoUmbrella-AddIpToDestinationList playbook|

<br>
<a name="postdeployment">

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Click the Microsoft Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for CiscoUmbrella connector API Connection

#### b. Configurations in Sentinel

Each Playbook requires a different type of configuration. Check documentation for each Playbook.

<a name="limitations">

## Known Issues and Limitations
