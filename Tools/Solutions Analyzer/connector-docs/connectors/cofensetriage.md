# Cofense Triage Threat Indicators Ingestion

| | |
|----------|-------|
| **Connector ID** | `CofenseTriage` |
| **Publisher** | Cofense |
| **Tables Ingested** | [`Cofense_Triage_failed_indicators_CL`](../tables-index.md#cofense_triage_failed_indicators_cl), [`Report_links_data_CL`](../tables-index.md#report_links_data_cl), [`ThreatIntelligenceIndicator`](../tables-index.md#threatintelligenceindicator) |
| **Used in Solutions** | [CofenseTriage](../solutions/cofensetriage.md) |
| **Connector Definition Files** | [CofenseTriage_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CofenseTriage/Data%20Connectors/CofenseTriageDataConnector/CofenseTriage_API_FunctionApp.json) |

The [Cofense-Triage](https://cofense.com/product-services/cofense-triage/) data connector provides the following capabilities: 

 1. CofenseBasedIndicatorCreator : 

 >* Get Threat Indicators from the Cofense Triage platform and create Threat Intelligence Indicators in Microsoft Sentinel. 

 > * Ingest Cofense Indicator ID and report links into custom logs table. 

 2. NonCofenseBasedIndicatorCreatorToCofense : 

 >* Get Non-Cofense Threat Intelligence Indicators from Microsoft Sentinel Threat Intelligence and create/update Indicators in Cofense Triage platform. 

 3. IndicatorCreatorToDefender : 

 >* Get Cofense Triage Threat Intelligence Indicators from Microsoft Sentinel Threat Intelligence and create/update Indicators in Microsoft Defender for Endpoints. 

 4. RetryFailedIndicators : 

 >* Get failed indicators from failed indicators files and retry creating/updating Threat Intelligence indicators in Microsoft Sentinel. 





 For more details of REST APIs refer to the below two documentations: 

 1. Cofense API documentation: 

> https://`<your-cofense-instance-name>`/docs/api/v2/index.html 

 2. Microsoft Threat Intelligence Indicator documentation: 

> https://learn.microsoft.com/rest/api/securityinsights/preview/threat-intelligence-indicator 

 3. Microsoft Defender for Endpoints Indicator documentation: 

> https://learn.microsoft.com/microsoft-365/security/defender-endpoint/ti-indicator?view=o365-worldwide

[← Back to Connectors Index](../connectors-index.md)
