# Tanium-UnquarantineHosts

## Overview

This playbook will use Tanium to remove a previously applied Tanium quarantine from hosts associated with a Microsoft Sentinel incident.

The results of the playbook will be added as comments to the incident: targeting results, action deployment status, and finally action results. The action results comment will wait for the action to expire and then check its results. By default the un-quarantine actions expire after thirty minutes.

![Tanium-UnquarantineHosts screenshot](images/Tanium-UnquarantineHosts.png)

## Prerequisites

Your Tanium Server will need the "IR Quarantine" content installed.

Sentinel incidents with associated hosts.

The "Tanium Threat Response Alerts" analytic rule will generate incidents from Tanium Threat Response Alerts with associated hosts from Tanium Threat Response alerts.

## Post-Deployment Instructions

You must authorize the API Connections used by this playbook after deployment.

1. Visit the playbook resource.
2. Under "Development Tools" (located on the sidebar), click "API Connections".
3. Ensure each connection has been authorized.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTanium%2FPlaybooks%2FTanium-UnquarantineHosts%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTanium%2FPlaybooks%2FTanium-UnquarantineHosts%2Fazuredeploy.json)

## Note

With the default deployment and configuration settings of the playbooks, your Tanium API Key is stored in a secure string workflow parameter. To update your Tanium API Key you must redeploy this playbook.

To allow Tanium API Key updates it is advised to use Azure Key Vault to securely store the Tanium API Key and update this playbook to use the Tanium API Key from the Key Vault instead of the secure string parameter.

Key Vault references

* [Key Vault | Microsoft Azure](https://azure.microsoft.com/services/key-vault/)
* [Azure Key Vault Connector reference | Microsoft Docs](https://docs.microsoft.com/connectors/keyvault/)
* [Secure access and data - Azure Logic Apps | Microsoft Docs](https://docs.microsoft.com/azure/logic-apps/logic-apps-securing-a-logic-app?tabs=azure-portal#secure-inputs-and-outputs-in-the-designer).

