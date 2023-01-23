# AbuseIPDB Logic Apps connector and playbook templates

<img src="./abuseipdb-logo.svg" alt="drawing" width="20%"/><br>

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

AbuseIPDB is a project that helps to check and report IP addresses involved in various categories of malicious attacks. It provides an API to check and report an IP address for malicious activity.

<a name="deployall">

## Custom Connectors + 3 Playbook templates deployment

This package includes:

* [Logic Apps custom connector for AbuseIPDB API](./AbuseIPDBAPIConnector)

* These three playbook templates leverage AbuseIPDB custom connector:
  * [Response – blacklist IP`s to tiIndicators](./Playbooks/AbuseIPDB-BlacklistIpToThreatIntelligence) - used to stream IOCs via Microsoft Graph Security tiIndicators API from the AbuseIPDB.
  * [Response - enrich incedent by IP info](./Playbooks/AbuseIPDB-EnrichIncidentByIPInfo) - get information about IP from AbuseIPDB and add to the incident comments.
  * [Response - Report IP to AbuseIPDB from the incident](./Playbooks/AbuseIPDB-ReportaIPsToAbuselPDBAfterCheckingByUserInMSTeams) - Report IP to AbuseIPDB from incident after user approval in Teams.

You can choose to deploy the whole package: connectors + all three playbook templates, or each one seperately from its specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAbuseIPDB%2FPlaybooks%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAbuseIPDB%2FPlaybooks%2Fazuredeploy.json)

# AbuseIPDB connector documentation 

<a name="authentication">

## Authentication

This connector supports Api Key authentication. When creating the connection for the custom connector, you will be asked to provide AbuseIPDB API Key.

<a name="prerequisites">

### Prerequisites in AbuseIPDB

For obtain API Key [follow the instructions](https://www.abuseipdb.com/api.html).

<a name="deployment">

### Deployment instructions

1. To deploy Custom Connectors and Playbooks, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters for deploying Custom Connectors and Playbooks

| Parameters | Description |
|----------------|--------------|
|**For Playbooks**|
|**AbuseIPDB-BlacklistIpToThreatIntelligence Playbook Name** | Enter the playbook name here (e.g. AbuseIPDB-BlacklistIpToThreatIntelligence)|
|**AbuseIPDB-EnrichIncidentByIPInfo Playbook Name** | Enter the playbook name here (e.g. AbuseIPDB-EnrichIncidentByIPInfo)|
|**AbuseIPDB-ReportaIPsToAbuselPDBAfterCheckingByUserInMSTeams Playbook Name** | Enter the playbook name here (e.g. AbuseIPDB-ReportaIPsToAbuselPDBAfterCheckingByUserInMSTeams)|
|**MSTeamsGroupId** | Value of TeamsGroupId parameter in AbuseIPDB-ReportaIPsToAbuselPDBAfterCheckingByUserInMSTeams playbook. Id of the Teams Group where the adaptive card will be posted.|
|**MSTeamsChannelId** | Value of TeamsChannelId parameter in AbuseIPDB-ReportaIPsToAbuselPDBAfterCheckingByUserInMSTeams playbook. Id of the Teams Channel where the adaptive card will be posted.|

<br>
<a name="postdeployment">

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Open playbook which has been deployed
2. Click API connection on left side blade
3. Click the Microsoft Sentinel connection resource
4. Click edit API connection
5. Click Authorize
6. Sign in
7. Click Save
8. Repeat steps for other connections

#### b. Configurations in Sentinel

Each Playbook requires a different type of configuration. Check documentation for each Playbook.

<a name="limitations">

## Known Issues and Limitations