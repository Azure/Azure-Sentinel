# Block IPs and Domains on Microsoft Defender for Endpoint with RecordedFuture
author: Glenn Wong, Recorded Future

# Overview
This playbook delivers active [C&C Server IPs](https://support.recordedfuture.com/hc/en-us/articles/360024113434-Security-Control-Feed-Command-and-Control "Recorded Future Support Page for Command and Control feeds") and [recently weaponized domains](https://support.recordedfuture.com/hc/en-us/articles/360024937813-Security-Control-Feed-Weaponized-Domains-and-URLs "Recorded Future Support Page for Weaponized Domains and URLs") to your Microsoft Defender for Endpoint for blocking and alerting.  These indicators come from a broad collection of sources (e.g., open source, dark web, technical sources, Insikt Group research), analyzed by Recorded Future's proprietary security graph, and delivered daily to Microsoft Defender via two interdependent Microsoft Azure Logic App playbooks.  For more information, see Recorded Future's webpage about the [Microsoft Defender for Endpoint integration](https://www.recordedfuture.com/integrations/defender/ "Recorded Future integration with Microsoft Defender for Endpoint").

# Dependencies
These playbooks use the ThreatIntelligenceIndicator table in Microsoft Graph Security.  Hence a successful deployment requires both Microsoft Graph Security, as well as Azure Sentinel, to enable the ThreatIntelligenceIndicator table.  In addition, this playbook uses a managed identity to access the API. You will need to add the playbook to the subscriptions or management group with Security Reader Role.

# Installation order
Due to internal Microsoft Logic Apps dependencies, you must deploy the first the playbook, **RecordedFuture_ImportToDefenderEndpoint**, _before_ the larger scope playbook, **RecordedFuture-TIforDefenderEndpoint**.


Links to deploy the RecordedFuture-ImportToDefenderEndpoint playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture-Block-IPs-and-Domains-on-Microsoft-Defender-for-Endpoint%2FRecordedFuture-ImportToDefenderEndpoint.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture-Block-IPs-and-Domains-on-Microsoft-Defender-for-Endpoint%2FRecordedFuture-ImportToDefenderEndpoint.json)

Links to deploy the RecordedFuture-TIforDefenderEndpoint playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture-Block-IPs-and-Domains-on-Microsoft-Defender-for-Endpoint%2FRecordedFuture-TIforDefenderEndpoint.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture-Block-IPs-and-Domains-on-Microsoft-Defender-for-Endpoint%2FRecordedFuture-TIforDefenderEndpoint.json)