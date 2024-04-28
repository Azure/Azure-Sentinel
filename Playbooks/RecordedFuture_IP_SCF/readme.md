# Recorded Future - IP - Command and Control Security Control Feed

Author: Recorded Future\
Link to [Recorded Future main readme](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Recorded%20Future/readme.md)

These playbooks leverage the Recorded Future API to automate the ingestion of Recorded Future IP [Command and Control - Security Control Feed](https://support.recordedfuture.com/hc/en-us/articles/360024113434-Security-Control-Feed-Command-and-Control), into the ThreatIntelligenceIndicator table, for prevention (block) actions in Microsoft Defender ATP. For additional information please visit [Recorded Future](https://www.recordedfuture.com/integrations/azure/).

## Permissions and Roles

The following Azure roles and permissions will be needed at various stages of installation. This install guide will specify at each step which specific permission is required

- Security Administrator (AD role, not the RBAC role)

- Global Administrator

- Logic app contributor

- Recorded Future Token
The **RecordedFuture_IP_SCF_ImportToDefenderATP** logic app uses Graph API and permissions **ThreatIndicators.ReadWrite.OwnedBy** are described in [Microsoft Graph Security Permissions](https://learn.microsoft.com/en-us/graph/api/tiindicator-submittiindicators?view=graph-rest-beta&tabs=http#permissions).

- [Microsoft Graph Security](https://learn.microsoft.com/en-us/graph/api/resources/tiindicator?view=graph-rest-beta)
- [Microsoft Graph Security & Azure Logic Apps](https://learn.microsoft.com/en-us/azure/connectors/connectors-integrate-security-operations-create-api-microsoft-graph-security)

## Dependencies

Playbooks takes a dependency on functionality like Azure Logic Apps, Azure Monitor Logs. Some of these dependencies either may be in [Preview](https://azure.microsoft.com/support/legal/preview-supplemental-terms/) state or might result in additional ingestion or operational costs.

- https://learn.microsoft.com/en-us/azure/azure-monitor/logs/quick-create-workspace
- https://learn.microsoft.com/en-us/azure/logic-apps/

How to use cost analysis to monitor your costs:

- https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/cost-analysis-common-uses
  
## Adjust Cadence of pulling Risk Lists

You can adjust the cadence in the Recurrence block of the IndicatorProcessor logic apps.
However, if you do so it is critical that you also adjust the expirationDateTime parameter in the final block of same logic app to be synchronized with the recurrence timing. Failure to do so can result in either

1. duplicate indicators or
1. having no active Recorded Future indicators the majority of the time.

## Installation order

Due to internal Microsoft Logic Apps dependencies, please deploy first the **RecordedFuture_IP_SCF_ImportToDefenderATP** playbook before the **RecordedFuture_IP_SCF_IndicatorProcessor** one.

## Installation links

Links to deploy the RecordedFuture_IP_SCF_ImportToDefenderATP playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_IP_SCF%2FRecordedFuture_IP_SCF_ImportToDefenderATP.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_IP_SCF%2FRecordedFuture_IP_SCF_ImportToDefenderATP.json)

Links to deploy the RecordedFuture_IP_SCF_IndicatorProcessor playbook template:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_IP_SCF%2FRecordedFuture_IP_SCF_IndicatorProcessor.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRecordedFuture_IP_SCF%2FRecordedFuture_IP_SCF_IndicatorProcessor.json)
