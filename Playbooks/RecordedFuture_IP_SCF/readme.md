# Recorded Future - IP - Command and Control Security Control Feed
author: Recorded Future

These playbooks leverage the Recorded Future API to automate the ingestion of Recorded Future IP [Command and Control - Security Control Feed](https://support.recordedfuture.com/hc/en-us/articles/360024113434-Security-Control-Feed-Command-and-Control), into the ThreatIntelligenceIndicator table, for prevention (block) actions in Microsoft Defender ATP. For additional information please visit [Recorded Future](https://www.recordedfuture.com/integrations/azure/).


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
Due to internal Microsoft Logic Apps dependencies, please deploy first the ImportToSentinel playbook before the IndicatorProcessor one.


Links to deploy the RecordedFuture_IP_SCF_IndicatorProcessor playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_IP_SCF%2FRecordedFuture_IP_SCF_IndicatorProcessor.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_IP_SCF%2FRecordedFuture_IP_SCF_IndicatorProcessor.json)

Links to deploy the RecordedFuture_IP_SCF_ImportToDefenderATP playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_IP_SCF%2FRecordedFuture_IP_SCF_ImportToDefenderATP.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_IP_SCF%2FRecordedFuture_IP_SCF_ImportToDefenderATP.json)