![DomainTools](./graphics/DomainTools.png)<br>
## DomainTools Iris Investigate Domain Playbook
## Table of Contents

1. [Overview](#overview)
1. [Deploy DomainTools Iris Investigate Domain Playbook](#deployplaybook)
1. [Authentication](#authentication)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)


<a name="overview">

## Overview
This playbook uses the DomainTools Iris Investigate API. Given a domain or set of domains associated with an incident this playbook returns all Iris Investigate data for those domains as comments in the incident.
 
Learn more about the Custom Connector via the https://docs.microsoft.com/en-us/connectors/domaintoolsirisinves or visit https://www.domaintools.com/integrations to request a Api key.

When a new Azure Sentinel Incident is created, this playbook gets triggered and performs below actions:

- It fetches all the Domain objects in the Incident.
- Iterates through the Domains objects and fetches the results from DomaintTools Iris Investigate for each Domain.
- All the details from DomainTools Iris Investigate will be added as comments in a tabular format.
- All the response attributes that have count value(Count of connected domains sharing this attribute) greater than 1 and less than "Pivot Threshold" parameter value in the playbook(default to 500), will have a link to get more details from DomainTools Iris Investigate API.

![Incident Comments](./graphics/comments1.png)
![Incident Comments](./graphics/comments2.png)

<a name="deployplaybook">

## Links to deploy the DomainTools Iris Investigate Domain Playbook

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FDomainTools%2FPlaybooks%2FDomainTools_Iris_Investigate-Domain_Playbook%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FDomainTools%2FPlaybooks%2FDomainTools_Iris_Investigate-Domain_Playbook%2Fazuredeploy.json)

<a name="authentication">

## Authentication
Authentication methods this connector supports- [API Key authentication](https://www.domaintools.com/integrations)

<a name="prerequisites">

## Prerequisites
- DomainTools Iris Investigate Api Key

<a name="deployment">

### Deployment instructions
- Deploy the playbooks by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
- Fill in the required parameters for deploying the playbook.

<a name="postdeployment">

### Post-Deployment instructions
#### a. Authorize connections 
Once deployment is complete, you will need to authorize each connection.
- Click the Azure Sentinel connection resource
- Click edit API connection
- Click Authorize
- Sign in
- Click Save
- Repeat steps for other connections such as DomainTools connector API Connection (For authorizing the DomainTools connector API connection, API Key and API secret needs to be provided.)
- Go to sentinel hook playbook to azure sentinel rules.
#### b. Configurations in Sentinel
- In Azure sentinel analytical rules should be configured to trigger an incident with risky user account. 
- Configure the automation rules to trigger the playbooks.
#### c. Managed Identity for Azure Sentinel Logic Apps connector
As a best practice, we used sentinel connection in playbooks that uses "ManagedSecurityIdentity". Please refer to [this document](https://techcommunity.microsoft.com/t5/microsoft-sentinel-blog/what-s-new-managed-identity-for-azure-sentinel-logic-apps/ba-p/2068204)
