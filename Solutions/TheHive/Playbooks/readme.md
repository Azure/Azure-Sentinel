# The Hive Logic Apps connector and playbook templates

<img src="./logo.png" alt="drawing" width="20%"/><br>

## Table of Contents

1. [Overview](#overview)
1. [Custom Connectors + 3 Playbook templates deployment](#deployall)
1. [Authentication](#importantnotes)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post-Deployment Steps](#postdeployment)
1. [References](#references)
1. [Known issues and limitations](#limitations)

<a name="overview">

# Overview

TheHive is a scalable, open source and free Security Incident Response Platform designed to make life easier for SOCs, CSIRTs, CERTs and any information security practitioner dealing with security incidents that need to be investigated and acted upon swiftly.

<a name="deployall">

## Custom Connectors + 3 Playbook templates deployment

This package includes:

* [Logic Apps custom connector for Vendor Product API](./VendorProductAPIConnector)


* These three playbook templates leverage Vendor Product custom connector:
  * [Create a Case](./Playbooks/TheHive-CreateCase) -  Pass incident from Sentinel to TheHive as case.
  * [Create an Alert](./Playbooks/TheHive-CreateAlert) -  Pass alert from Sentinel to The Hive.
  * [Lock User](./Playbooks/TheHive-LockUser) - Lock the user in the Hive by user id or name.

You can choose to deploy the whole package: connectors + all three playbook templates, or each one seperately from its specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTheHive%2FPlaybooks%2Fazuredeploy.json)
[![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTheHive%2FPlaybooks%2Fazuredeploy.json)

# The Hive connectors documentation 

<a name="authentication">

## Authentication

This connector supports Basic authentication.
When creating the connection for the custom connector, you will be asked to provide user and password which you generated in
TheHive web interface.

<a name="prerequisites">

### Prerequisites in The Hive

TheHive connector uses [On-Premises Data Gateway](https://docs.microsoft.com/data-integration/gateway/service-gateway-onprem).
Therefore [installation of the On-Premises Data Gateway](https://docs.microsoft.com/azure/logic-apps/logic-apps-gateway-install) and [creation of the On-Premises Data Gateway resource](https://docs.microsoft.com/azure/logic-apps/logic-apps-gateway-connection#create-azure-gateway-resource) are required.

<a name="deployment">

### Deployment instructions 

1. To deploy Custom Connectors and Playbooks, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters for deploying Custom Connectors and Playbooks

| Parameters              | Description                                             |
|-------------------------|---------------------------------------------------------|
| **For Connector**       |                                                         |
| **Connector Name**      | Logic App Connector name for TheHive                    |
| **API Hostname**        | Hostname of TheHive instance                            |
| **API Port**            | Port number of TheHive API. By default 9000.            |
| **Http scheme**         | Http scheme for TheHive API.                            |
| **For Playbooks**       |
| **TheHive-CreateAlert** | Enter the playbook name here (e.g. TheHive-CreateAlert) |
| **TheHive-CreateCase**  | Enter the playbook name here (e.g. TheHive-CreateCase)  |
| **TheHive-LockUser**    | Enter the playbook name here (e.g. TheHive-LockUser)    |
| **onPremiseGatewayName** | Provide the On-premises data gateway that will be used with The Hive connector. Data gateway should be deployed under the same subscription and resource group as playbooks. |

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
6. Repeat steps for other connections

#### b. Configurations in Sentinel

Each Playbook requires a different type of configuration. Check documentation for each Playbook.

<a name="limitations">

## Known Issues and Limitations