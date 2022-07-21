# URLhaus Logic Apps connector and playbook templates

<img src="./urlhaus-logo.png" alt="drawing" width="20%"/><br>

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

Beside the APIs documented on URLhaus that serves various feeds and lists, abuse.ch also offers a dedicated API that allows to gather information on a specific URL, file hash or host from URLhaus through an automated way. It is also possible to retrieve a payload (malware sample) URLhaus has collected from malware URLs it tracks.

<a name="deployall">

## Custom Connectors + 3 Playbook templates deployment

This package includes:

* [Logic Apps custom connector for URLhaus API](./URLhausAPIConnector)

* These three playbook templates leverage URLhaus custom connector:
  * [Response - enrich incedent by hash info](./Playbooks/URLhaus-CheckHashAndEnrichIncident) - get information about hash from URLhaus and add to the incident comments.
  * [Response - enrich incedent by hostname info](./Playbooks/URLhaus-CheckHostAndEnrichIncident) - get information about hostname from URLhaus and add to the incident comments.
  * [Response - enrich incedent by URL info](./Playbooks/URLhaus-CheckURLAndEnrichIncident) - get information about URL from URLhaus and add to the incident comments.

You can choose to deploy the whole package: connectors + all three playbook templates, or each one seperately from its specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Faverbn%2FAzure-Sentinel%2FURLhaus-Connector-and-Playbooks%2FSolutions%2FURLhaus%2FPlaybooks%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Faverbn%2FAzure-Sentinel%2FURLhaus-Connector-and-Playbooks%2FSolutions%2FURLhaus%2FPlaybooks%2Fazuredeploy.json)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FURLhaus%2FPlaybooks%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FURLhaus%2FPlaybooks%2Fazuredeploy.json)

# URLhaus connector documentation 

<a name="authentication">

## Authentication

No authentication needed.

<a name="deployment">

### Deployment instructions

1. To deploy Custom Connectors and Playbooks, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters for deploying Custom Connectors and Playbooks

| Parameters | Description |
|----------------|--------------|
|**For Playbooks**|
|**URLhaus-CheckHashAndEnrichIncident Playbook Name** | Enter the playbook name here (e.g. URLhaus-CheckHashAndEnrichIncident)|
|**URLhaus-CheckHostAndEnrichIncident Playbook Name** | Enter the playbook name here (e.g. URLhaus-CheckHostAndEnrichIncident)|
|**URLhaus-CheckURLAndEnrichIncident Playbook Name** | Enter the playbook name here (e.g. URLhaus-CheckURLAndEnrichIncident)|
<br>
<a name="postdeployment">

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Open playbook which has been deployed
2. Click API connection on left side blade
3. Click the Azure Sentinel connection resource
4. Click edit API connection
5. Click Authorize
6. Sign in
7. Click Save
8. Repeat steps for other connections

#### b. Configurations in Sentinel

Each Playbook requires a different type of configuration. Check documentation for each Playbook.

<a name="limitations">

## Known Issues and Limitations