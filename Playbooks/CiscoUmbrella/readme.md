# Cisco Umbrella Logic Apps connector and playbook templates

<img src="./cisco-logo.png" alt="drawing" width="20%"/><br>

## Table of Contents

1. [Overview](#overview)
1. [Deploy Custom Connectors + 3 Playbook templates](#deployall)
1. [Authentication](#importantnotes)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)
1. [References](#references)
1. [Known issues and limitations](#limitations)

<a name="overview">

# Overview

Cisco Umbrella is a Cloud driven Secure Internet Gateway that provides protection from Internet based threats, for users wherever they go.

<a name="deployall">

## Deploy Custom Connectors + 3 Playbook templates

This package includes:

* [Logic Apps custom connector for Cisco Umbrella Enforcement API](./CiscoUmbrellaEnforcementAPIConnector)
* [Logic Apps custom connector for Cisco Umbrella Investigate API](./CiscoUmbrellaInvestigateAPIConnector)
* [Logic Apps custom connector for Cisco Umbrella Management API](./CiscoUmbrellaManagementAPIConnector)
* [Logic Apps custom connector for Cisco Umbrella Network Device Management API](./CiscoUmbrellaNetworkDeviceManagementAPIConnector)

* Three playbook templates leverage Cisco Umbrella custom connectors:
  * [Response – assign policy to identity](./Playbooks/CiscoUmbrella-AssignPolicyToIdentity) - assigns a new DNS or web policy (provided on the playbook deplyment step) to an identity.
  * [Response - block domain](./Playbooks/CiscoUmbrella-BlockDomain) - add domains to a customer's domain lists.
  * [Enrichment - add security info about domain to incident](./Playbooks/CiscoUmbrella-GetDomainInfo) - collect security information about domains and post it as incident comment.

You can choose to deploy the whole package: connectors + all three playbook templates, or each one seperately from it's specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2Fcisco_umbrella_playbooks%2FPlaybooks%2FCiscoUmbrella%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2Fcisco_umbrella_playbooks%2FPlaybooks%2FCiscoUmbrella%2Fazuredeploy.json)

# Cisco Umbrella connectors documentation 

<a name="authentication">

## Authentication

Each Logic Apps custom connector uses different type of authentication. Check documentation of each connector.

<a name="prerequisites">

### Prerequisites in Cisco Umbrella

Each Logic Apps custom connector requires different type of credentials. Check documentation of each connector.

<a name="deployment">

### Deployment instructions 

1. Deploy the Custom Connectors and playbooks by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters for deploying custom connectors and playbooks

| Parameters | Description |
|----------------|--------------|
|**For Playbooks**|
|**CiscoUmbrella-AssignPolicyToIdentity Playbook Name** | Enter the playbook name here (e.g. CiscoUmbrella-AssignPolicyToIdentity)|
|**CiscoUmbrella-BlockDomain Playbook Name** | Enter the playbook name here (e.g. CiscoUmbrella-BlockDomain)|
|**CiscoUmbrella-GetDomainInfo Playbook Name** | Enter the playbook name here (e.g. CiscoUmbrella-GetDomainInfo)|
|**PolicyId** | ID of the DNS or web policy to use in CiscoUmbrella-AssignPolicyToIdentity playbook|

<br>
<a name="postdeployment">

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, you will need to authorize each connection.

1. Click the Azure Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for CiscoUmbrella connector API Connection

#### b. Configurations in Sentinel

Each playbook requires different type of configuration. Check documentation of each playbook.

<a name="limitations">

## Known Issues and Limitations
