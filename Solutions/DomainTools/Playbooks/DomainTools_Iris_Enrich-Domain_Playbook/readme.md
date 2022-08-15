# DomainTools Iris Enrich Domain Playbook

![DomainTools](./graphics/DomainTools.png)<br>

## Table of Contents

1. [Overview](#overview)
1. [Deploy DomainTools Iris Enrich Domain Playbook](#deployplaybook)
1. [Authentication](#authentication)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)


<a name="overview">

# Overview
This playbook uses the DomainTools Iris Enrich API, which is more suited to high-volume API lookups than Iris Investigate and is able to provide domain infrastructure information for a domain or set of domains associated with an incident. If your account is provisioned for Iris Enrich, use the Iris Enrich endpoint to return all Iris Enrich data for a given domain or set of domains.
 
Learn more about the Custom Connector via the https://docs.microsoft.com/en-us/connectors/domaintoolsirisenric or visit https://www.domaintools.com/integrations to request a Api key.

When a new Azure Sentinel Incident is created, this playbook gets triggered and performs below actions:

- It fetches all the Domain objects in the Incident.
- Iterates through the Domains objects and fetches the results from DomaintTools Iris Enrich for each Domain.
- All the details from DomainTools Iris Enrich will be added as comments in a tabular format.

![Incident Comments](./graphics/comments1.png)(./graphics/comments2.png)

<a name="deployplaybook">

## Links to deploy the DomainTools Iris Enrich Domain Playbook:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FDomainTools%2FPlaybooks%2FDomainTools_Iris_Enrich-Domain_Playbook_Template%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FDomainTools%2FPlaybooks%2FDomainTools_Iris_Enrich-Domain_Playbook_Template%2Fazuredeploy.json)


<a name="authentication">

## Authentication
Authentication methods this connector supports- [API Key authentication](https://www.domaintools.com/integrations)

<a name="prerequisites">

## Prerequisites for using and deploying playbook
- DomainTools Iris Enrich Api Key

<a name="deployment">

#### Deployment instructions
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
As a best practice, we used sentinel connection in playbooks that uses "ManagedSecurityIdentity". Please refer [this](https://techcommunity.microsoft.com/t5/microsoft-sentinel-blog/what-s-new-managed-identity-for-azure-sentinel-logic-apps/ba-p/2068204)
