# Azure firewall Logic Apps connector

![Azure Firewall](./AzureFirewallCustomConnector.png)<br>
## Table of Contents

1. [Overview](#overview)
1. [Actions supported by Firewall custom connector](#actions)
1. [Deployment](#deployment)
1. [Authentication](#Authentication)

<a name="overview">

## Overview
Azure Firewall is a cloud-based network security service, sitting at the edge of the Azure virtual network resources, to provide additional security beyond what is offered by NSGs. <br>
This integration allows to automate response to Microsoft Sentinel incidents which contains IPs. <br>
I contains actions that work on: IP Groups, Azure Firewall and Azure Firewall Policy.


<a name="actions">

## Actions supported by Firewall custom connector

| Component | Description |
| --------- | -------------- |
| **Create or Update a firewall** | Action used to create and update a firewall|
| **Add a new rule** | Action used to add new rules.|
| **Add an IP address to an existing rule** | Action used to add an IP address to an existing rule of the Firewall.|
| **Update Threat Intel allow list** |Update Threat intel allow list of the firewall|
| **Update Tags** |Update Tags.|
| **Get Firewall** | action used to fetch list of firewall details|
| **List All Azure Firewalls in Subscription** | Action used to fetch the details of Azure Firewalls in Subscription.|
| **List Azure Firewalls in Resource Group** | Action used to fetch the list of azure Firewall in the resourse group. |
| **Get firewall policy information** | Action used to fetch the details of firewall policy information. |
| **Deletes the specified Firewall Policy** | Action used to delete the specified the firewall policy. |
| **Lists all Firewall Policies in a resource group** | Action used to lists all Firewall Policies in a resource group. |
| **Gets all the Firewall Policies in a subscription** | Action used to gets all the Firewall Policies in a subscription. |
| **Creates or updates the specified Firewall Policy** | Action used to creates or updates the specified Firewall Policy. |
| **Gets the specified ipGroups** | Action used to gets the specified ipGroups. |
| **Deletes the specified IP Groups** | Action used to deletes the specified IP Groups. |
| **Creates or updates an IP Groups in a specified resource group** | Action used to creates or updates an IP Groups in a specified resource group. |
| **Updates tags of an IpGroups resource** | Action used to updates tags of an IpGroups resource. |
| **Gets all IP Groups in a subscription** | Action used to gets all IP Groups in a subscription. |
| **Ip Groups - List By Resource Group** | Action used to Ip Groups - List By Resource Group. |

<a name="deployment">

## Deployment instructions 

Prior using this custom connector, it should be deployed in the Resource Group where the playbooks that will include it are located.
<br>
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required paramteres:
    * Connector name: Please enter the custom connector(ex:contoso firewall connector)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAzure%2520Firewall%2FPlaybooks%2FAzureFirewallConnector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAzure%2520Firewall%2FPlaybooks%2FAzureFirewallConnector%2Fazuredeploy.json)


<a name="authentication">

## Authentication
This connector supports Service Principal authentication type.
### Microsoft Entra ID Service principal
To use your own application with the Microsoft Sentinel connector, perform the following steps:

1. Register the application with Microsoft Entra ID and create a service principal. [Learn how](https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal#register-an-application-with-azure-ad-and-create-a-service-principal).

1. Get credentials (for future authentication).
    In the registered application blade, get the application credentials for later signing in:

    - Tenant Id: under **Overview**
    - Client ID: under **Overview**
    - Client secret: under **Certificates & secrets**.

1. Grant permissions to Azure Firewall, IP Groups or Azure Firewall Policies.

    - In the relevant resources of the above, go to Settings -> Access control (IAM)

    - Select **Add role assignment**.

    - Select the role you wish to assign to the application: **Contributor** role.

    - Find the required application and save. By default, Microsoft Entra ID applications aren't displayed in the available options. To find your application, search for the name and select it.

1. Authenticate

    In this step we use the app credentials to authenticate to the Sentinel connector in Logic Apps.

    In the custom connector for Azure Firewall, fill in the required parameters (can be found in the registered application blade)
        - Tenant Id: under **Overview**
        - Client Id: under **Overview**
        - Client Secret: under **Certificates & secrets**
