# Comment-OriginAlertURL
author: Jordan Ross

This playbook will add a comment to Sentinel Incidents with the Origin Alert URL for Incidents related to Azure Advanced Threat Protection, Microsoft Cloud App Security, and Microsoft Defender Advanced Threat Protection. With this URL users will be able to unify and expand their investigation experience and view data such as related activities from the detection source (e.g., MCAS). 

**NOTE:  This playbook requires the enablement of at least one of the following data connections: AATP, MCAS, or MDATP. This playbook uses a managed identity to access the API.  You will need to add the playbook to the subscriptions or management group with Security Reader Role**

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FComment-OriginAlertURL%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FComment-OriginAlertURL%2Fazuredeploy.json)