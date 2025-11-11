# Block-IPs-on-MDATP-Using-GraphSecurity
author: Chi Nguyen

This playbook will get the IP information from an Azure Sentinel incident when the security incident triggers in Azure Sentinel. The IP info will then be sent to a security analyst over email. The analyst will either approve or reject the blocking of the IP. If approved, the IP will then be pushed to be blocked on Microsoft Defender ATP using the Graph Security TI indicator Post method.

**NOTE**: **This playbook requires the enablement of at least one of the following data connections: Azure Sentinel, Office 365 Outlook, Microsoft Graph Security. This playbook uses a managed identity to access the API. You will need to add the playbook to the subscriptions or management group with Security Reader Role.**

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FBlock-IPs-on-MDATP-Using-GraphSecurity%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FBlock-IPs-on-MDATP-Using-GraphSecurity%2Fazuredeploy.json)