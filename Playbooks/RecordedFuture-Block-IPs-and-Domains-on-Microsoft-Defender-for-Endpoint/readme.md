# Block IPs and Domains on Microsoft Defender for Endpoint with RecordedFuture
author: Recorded Future

# Overview
This playbook delivers active [C&C Server IPs](https://support.recordedfuture.com/hc/en-us/articles/360024113434-Security-Control-Feed-Command-and-Control "Recorded Future Support Page for Command and Control feeds") and [recently weaponized domains](https://support.recordedfuture.com/hc/en-us/articles/360024937813-Security-Control-Feed-Weaponized-Domains-and-URLs "Recorded Future Support Page for Weaponized Domains and URLs") to your Microsoft Defender for Endpoint for blocking and alerting.  These indicators come from a broad collection of sources (e.g., open source, dark web, technical sources, Insikt Group research), analyzed by Recorded Future's proprietary security graph, and delivered daily to Microsoft Defender via two interdependent Microsoft Azure Logic App playbooks.  For more information, see Recorded Future's webpage about the [Microsoft Defender for Endpoint integration](https://www.recordedfuture.com/integrations/defender/ "Recorded Future integration with Microsoft Defender for Endpoint").

# Dependencies
These playbooks use Microsoft Graph Security and stores indicators in the ThreatIntelligenceIndicator table. Hence a successful deployment requires Microsoft Graph Security enabled. This playbook uses a managed identity to access the API. You will need to add the playbook to the subscriptions or management group with Security Reader Role.

[Microsoft Graph Security](https://learn.microsoft.com/en-us/graph/api/resources/tiindicator?view=graph-rest-beta)

[Microsoft Graph Security & Azure Logic Apps](https://learn.microsoft.com/en-us/azure/connectors/connectors-integrate-security-operations-create-api-microsoft-graph-security)


This playbook takes a dependency on functionality like Azure Logic Apps, Azure Monitor Logs. Some of these dependencies either may be in [Preview](https://azure.microsoft.com/support/legal/preview-supplemental-terms/) state or might result in additional ingestion or operational costs.

- https://learn.microsoft.com/en-us/azure/azure-monitor/logs/quick-create-workspace
- https://learn.microsoft.com/en-us/azure/logic-apps/

Use const analysis to monitor your costs
- https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/cost-analysis-common-uses

# Adjust Cadence of pulling Risk Lists
You can adjust the cadence in the Recurrence block of the IndicatorProcessor logic apps.
However, if you do so it is critical that you also adjust the expirationDateTime parameter in the final block of same logic app to be synchronized with the recurrence timing. Failure to do so can result in either 
a) duplicate indicators or 
b) having no active Recorded Future indicators the majority of the time. 

If you are unsure of how to do this, please consult Recorded Future Professional Services.

# Installation order
Due to internal Microsoft Logic Apps dependencies, you must deploy the first the playbook, **RecordedFuture_ImportToDefenderEndpoint**, _before_ the larger scope playbook, **RecordedFuture-TIforDefenderEndpoint**.


Links to deploy the RecordedFuture-ImportToDefenderEndpoint playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture-Block-IPs-and-Domains-on-Microsoft-Defender-for-Endpoint%2FRecordedFuture-ImportToDefenderEndpoint.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture-Block-IPs-and-Domains-on-Microsoft-Defender-for-Endpoint%2FRecordedFuture-ImportToDefenderEndpoint.json)

Links to deploy the RecordedFuture-TIforDefenderEndpoint playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture-Block-IPs-and-Domains-on-Microsoft-Defender-for-Endpoint%2FRecordedFuture-TIforDefenderEndpoint.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture-Block-IPs-and-Domains-on-Microsoft-Defender-for-Endpoint%2FRecordedFuture-TIforDefenderEndpoint.json)

