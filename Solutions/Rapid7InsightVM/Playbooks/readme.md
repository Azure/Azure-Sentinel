# Rapid7 InsightVM Logic Apps connector and playbook templates

<img src="./logo.png" alt="drawing" width="20%"/><br>

## Table of Contents

1. [Overview](#overview)
1. [Custom Connectors + 3 Playbook templates deployment](#deployall)
1. [Authentication](#authentication)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post-Deployment Steps](#postdeployment)

<a name="overview">

# Overview

Rapid7 InsightVM is a vulnerability management tool that brings together Rapid7’s library of vulnerability research, exploit knowledge, global attacker behavior, Internet-wide scanning data, exposure analytics, and real-time reporting. 

<a name="deployall">

## Custom Connectors + 3 Playbook templates deployment

This package includes:

* [Logic Apps custom connector for Rapid7 InsightVM Cloud Integrations API](./Rapid7InsightVMCloudAPIConnector)


* These three playbook templates leverage Rapid7 InsightVM custom connector:
  * [Rapid7InsightVM-EnrichIncidentWithAssetInfo](./Playbooks/Rapid7InsightVM-EnrichIncidentWithAssetInfo)
  * [Rapid7InsightVM-EnrichVulnerabilityInfo](./Playbooks/Rapid7InsightVM-EnrichVulnerabilityInfo)
  * [Rapid7InsightVM-RunScan](./Playbooks/Rapid7InsightVM-RunScan)

You can choose to deploy the whole package: connectors + all three playbook templates, or each one seperately from its specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRapid7InsightVM%2FPlaybooks%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRapid7InsightVM%2FPlaybooks%2Fazuredeploy.json)

# Rapid7 InsightVM connectors documentation 

<a name="authentication">

## Authentication

* API Key authentication

<a name="prerequisites">

### Prerequisites in Rapid7 InsightVM

To get Rapid7 InsightVM API key, follow the instructions in the [documentation](https://docs.rapid7.com/insight/managing-platform-api-keys/).

<a name="deployment">

### Deployment instructions 

1. To deploy Custom Connectors and Playbooks, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters for deploying Custom Connectors and Playbooks

| Parameters | Description |
|----------------|--------------|
|**For Connector**|
|**Connector Name**| Enter the Rapid7 InsightVM Logic App connector name here |
|**Insight Platform Region** | The region indicates the geo-location of the Insight Platform. |
|**For Playbooks**|
|**Rapid7InsightVM-EnrichIncidentWithAssetInfo Playbook Name** | Name of the Playbook |
|**Rapid7InsightVM-EnrichVulnerabilityInfo Playbook Name** | Name of the Playbook |
|**Rapid7InsightVM-RunScan Playbook Name** | Name of the Playbook |
|**TeamsGroupId** | Id of the Teams Group where the adaptive card will be posted (for playbook Rapid7InsightVM-RunScan). |
|**TeamsChannelId** | Id of the Teams Channel where the adaptive card will be posted (for playbook Rapid7InsightVM-RunScan). |

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
