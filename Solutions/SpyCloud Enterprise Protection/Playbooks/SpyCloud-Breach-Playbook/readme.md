# SpyCloud Enterprise Breach Playbook 

![SpyCloud Enterprise](images/logo.png)

## Table of Contents

1. [Overview](#overview)
3. [Prerequisites](#prerequisites)
4. [Deployment](#deployment)
5. [Post Deployment Steps](#postdeployment)


<a name="overview">

## Overview
This playbook gets triggered when an incident is created from the "SpyCloud Breach Rule" and can perform the following actions

- Check if the breached password length is >= the minimum required by the organization. If not, exit the playbook. 
- Check if the user is currently an active employee. If not, exit the playbook. 
- Check if the exposed password is in use on the network (check AD, check Okta, check Ping, check G-Suite, etc. 
- If the password is in use in one of the checked systems, perform a password reset, raise an incident, etc. 


<a name="prerequisites">

## Prerequisites
- A SpyCloud Enterprise API Key.
- SpyCloud Enterprise custom connector needs to be deployed prior to the deployment of this playbook, in the same resource group and region. Relevant instructions can be found on the connector doc page.
- SpyCloud-Monitor-Watchlist-Data-Playbook needs to be deployed prior to the deployment of this playbook, in the same resource group and region. Relevant instructions can be found on the playbook doc page.

<a name="deployment">

## Deployment Instructions
- Deploy the playbooks by clicking on the "Deploy to Azure" button. This will take you to the ARM Template Wizard.
- Fill in the required parameters for deploying the playbook.
  ![deployment](images/deployment.png)
- Click "Review + create". Once the validation is successful, click on "Create".

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSpyCloud%20Enterprise%20Protection%2FPlaybooks%2FSpyCloud-Breach-Playbook%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSpyCloud%20Enterprise%20Protection%2FPlaybooks%2FSpyCloud-Breach-Playbook%2Fazuredeploy.json)

<a name="postdeployment">

## Post Deployment Instructions
### Authorize connections
Once deployment is complete, you will need to authorize each connection:
- As a best practice, we have used the Sentinel connection in Logic Apps that use "ManagedSecurityIdentity" permissions. Please refer to [this document](https://techcommunity.microsoft.com/t5/microsoft-sentinel-blog/what-s-new-managed-identity-for-azure-sentinel-logic-apps/ba-p/2068204) and provide permissions to the Logic App accordingly.
- Provide connection details for the SpyCloud Enterprise Custom Connector.
- Save the Logic App. If the Logic App prompts any missing connections, please update the connections similarly.
### b.Configurations in Sentinel:
- In Azure Sentinel, configure the SpyCloud Breach rule automation rules to trigger this playbook.
