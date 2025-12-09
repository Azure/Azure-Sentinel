# CofenseTriage

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Cofense Support |
| **Support Tier** | Partner |
| **Support Link** | [https://cofense.com/contact-support/](https://cofense.com/contact-support/) |
| **Categories** | domains |
| **First Published** | 2023-03-24 |
| **Last Updated** | 2023-03-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CofenseTriage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CofenseTriage) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Cofense Triage Threat Indicators Ingestion](../connectors/cofensetriage.md)

**Publisher:** Cofense

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

| | |
|--------------------------|---|
| **Tables Ingested** | `Cofense_Triage_failed_indicators_CL` |
| | `Report_links_data_CL` |
| | `ThreatIntelligenceIndicator` |
| **Connector Definition Files** | [CofenseTriage_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CofenseTriage/Data%20Connectors/CofenseTriageDataConnector/CofenseTriage_API_FunctionApp.json) |

[→ View full connector details](../connectors/cofensetriage.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Cofense_Triage_failed_indicators_CL` | [Cofense Triage Threat Indicators Ingestion](../connectors/cofensetriage.md) |
| `Report_links_data_CL` | [Cofense Triage Threat Indicators Ingestion](../connectors/cofensetriage.md) |
| `ThreatIntelligenceIndicator` | [Cofense Triage Threat Indicators Ingestion](../connectors/cofensetriage.md) |

[← Back to Solutions Index](../solutions-index.md)
