# ConnectorName Logic Apps connector

![ConnectorName](./AzureFirewallCustomConnector.png)<br>
## Table of Contents

1. [Overview](#overview)
1. [Actions supported by connectorName custom connector](#actions)
1. [Deployment](#deployment)
1. [Authentication](#Authentication)

<a name="overview">

## Overview
General info about this product and the core values of this integration. <br>


<a name="actions">

## Actions supported by connectorName custom connector

| Component | Description |
| --------- | -------------- |
| **Action Name** | 1-2 sentences about this action|


<a name="deployment">

## Deployment instructions 


<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2F --- path ---azuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>

<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2F --- path ---azuredeploy.json" target="_blank">
   <img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>    
</a>


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