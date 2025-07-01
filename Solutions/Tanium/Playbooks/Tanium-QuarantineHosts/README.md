# Tanium-QuarantineHosts

## Overview

This playbook will use Tanium to quarantine any hosts associated with a Microsoft Sentinel incident. After the quarantine request has been made, it will wait for the quarantine action to expire and then check its results.

The results of the playbook will be added as comments to the incident:
1. The hosts that will be targeted
2. The quarantine action(s)' deployment status
3. The results of the quarantine action(s)

![Tanium-QuarantineHosts screenshot](images/Tanium-QuarantineHosts.png)

## Prerequisites
- Sentinel incidents with associated hosts running the Tanium client   
If this playbook it run against an incident with 1 or more hosts that are not running the Tanium client, then Tanium will not be able to provide information for those host(s). If the incident only contains hosts that are not running the Tanium client then a comment will be placed on the incident indicating that, and the playbook will exit early.

> [!TIP]
> Leverage the "Tanium Threat Response Alerts" analytics rule to generate Sentinel incidents for an Threat Response Alert from Tanium.

- A [Tanium API Token](https://help.tanium.com/bundle/ug_console_cloud/page/platform_user/console_api_tokens.html)   
A Tanium API token, granting access to your Tanium environment is required to make the necessary queries against the Tanium API.  

- An Azure Integration Account   
Required to execute javascript needed to prepare query filters for Tanium API Gateway HTTP requests

- Tanium Threat Response 4.7+ Module   
Tanium Threat Response must be installed and running your Tanium environment and must be version 4.7 or higher. If you are running a lower version see See [Tanium Playbooks](https://help.tanium.com/bundle/ConnectAzureSentinel/page/Integrations/MSFT/ConnectAzureSentinel/Get_to_know_our_Content.htm#_Tanium_Playbooks) for more information.

- Permission to Assign Roles to the Resource Group   
For this playbook to successfully run it must have the Microsoft Sentinel Contributor role at the Resource Group scope. This is added as part of this ARM template, and therefore requires the user who is creating the playbook to have `Microsoft.Authorization/roleAssignments/write` on the resource group. Some examples of roles that meet this criteria for the user include:
  - Owner
  - User Access Administrator
  - Role Based Access Control Administrator
  - Global Admininstrator 

## Get the Template
Use the links below to create the playbook from our template.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTanium%2FPlaybooks%2FTanium-QuarantineHosts%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTanium%2FPlaybooks%2FTanium-QuarantineHosts%2Fazuredeploy.json)

## Note

With the default deployment and configuration settings of the playbooks, your Tanium API Key is stored in a secure string workflow parameter. To update your Tanium API Key you must redeploy this playbook.

To allow Tanium API Key updates it is advised to use Azure Key Vault to securely store the Tanium API Key and update this playbook to use the Tanium API Key from the Key Vault instead of the secure string parameter.

Key Vault references

* [Key Vault | Microsoft Azure](https://azure.microsoft.com/services/key-vault/)
* [Azure Key Vault Connector reference | Microsoft Docs](https://docs.microsoft.com/connectors/keyvault/)
* [Secure access and data - Azure Logic Apps | Microsoft Docs](https://docs.microsoft.com/azure/logic-apps/logic-apps-securing-a-logic-app?tabs=azure-portal#secure-inputs-and-outputs-in-the-designer).

