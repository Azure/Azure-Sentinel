# ConnectorName Logic Apps connector and playbook templates

![ConnectorName](./connectorName/logo.png)<br>

## Table of Contents

1. [Overview](#overview)
1. [Deploy Custom Connector + 3 Playbook templates](#deployall)
1. [Authentication](#authentication)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)
1. [References](#references)


<a name="overview">

## Overview
General info about this product and the core values of this integration. <br>
It also contains 3 playbook templates, ready to quick use, that allow ...

<a name="deployall">

## Deploy Custom Connector + 3 Playbook templates
This package includes:
* Custom connector for ConnectorName
* Three playbook templates leverage ConnectorName custom connector

You can choose to deploy the whole package: connector + all three playbook templates (below buttons), or each one seperately from it's specific folder.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2F --- path ---azuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>

<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2F --- path ---azuredeploy.json" target="_blank">
   <img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>    
</a>


# connectorName connector documentation 

<a name="authentication">

## Authentication
This connector supports the following authentication types:
* Basic Authentication
* OAuth User sign in
* Service Principal
* API Key
* Logic Apps gateway

###  Azure Active Directory Service principal (example)
To use your own application with the Azure Sentinel connector, perform the following steps:

1. Register the application with Azure AD and create a service principal. [Learn how](https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal#register-an-application-with-azure-ad-and-create-a-service-principal).

1. Get credentials (for future authentication).

    In the registered application blade, get the application credentials for later signing in:

    - Tenant Id: under **Overview**
    - Client ID: under **Overview**
    - Client secret: under **Certificates & secrets**.

1. Grant permissions to ConnectorName:

    - In the relevant resources of the above, go to Settings -> Access control (IAM)

    - Select **Add role assignment**.

    - Select the role you wish to assign to the application: **Contributor** role.

    - Find the required application and save. By default, Azure AD applications aren't displayed in the available options. To find your application, search for the name and select it.

1. Authenticate

    In this step we use the app credentials to authenticate to the Sentinel connector in Logic Apps.

    In the custome connector for ConnectorName, fill in the required parameters (can be found in the registered application blade)
        - Tenant Id: under **Overview**
        - Client Id: under **Overview**
        - Client Secret: under **Certificates & secrets**

<a name="prerequisites">

### Prerequisites for using and deploying Custom Connector
1. Register an AAD app and capture the ClientID, SecretKey and TenantID
1. Playbook templates leverage VirusTotal for IP enrichment. To use this VirusTotal capabilities,generate a Virus Total API key. Refer this link [ how to generate the API Key](https://developers.virustotal.com/v3.0/reference#getting-started)

<a name="deployment">

### Deployment instructions 
1. Deploy the Custom Connector and playbooks by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required parameteres:

Special configutations/parameters for Playbook templates

<a name="postdeployment">

### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, you will need to authorize each connection. For each API connection resource:
 1. Click edit API connection
 1. Click Authorize
 1. Sign in
 1. Click Save
 1. Repeat steps for other connection.

#### b. Configurations in Azure Sentinel
1. Enable Azure Sentinel Analytics rules that create alerts and incidents which includes the relevant entities.
1. Configure automation rule(s) to trigger the playbooks.


<a name="references">

## Learn more
*  [Relevant API docs](url)
