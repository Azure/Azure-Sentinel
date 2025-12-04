# CofenseIntelligence

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Cofense Support |
| **Support Tier** | Partner |
| **Support Link** | [https://cofense.com/contact-support/](https://cofense.com/contact-support/) |
| **Categories** | domains |
| **First Published** | 2023-05-26 |
| **Last Updated** | 2024-05-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CofenseIntelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CofenseIntelligence) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Cofense Intelligence Threat Indicators Ingestion](../connectors/cofenseintelligence.md)

**Publisher:** Cofense

The [Cofense-Intelligence](https://cofense.com/product-services/phishing-intelligence/) data connector provides the following capabilities: 

 1. CofenseToSentinel : 

 >* Get Threat Indicators from the Cofense Intelligence platform and create Threat Intelligence Indicators in Microsoft Sentinel. 

 2. SentinelToDefender : 

 >* Get Malware from Cofense Intelligence and post to custom logs table. 

 3. CofenseIntelligenceMalware : 

 >* Get Cofense Intelligence Threat Intelligence Indicators from Microsoft Sentinel Threat Intelligence and create/update Indicators in Microsoft Defender for Endpoints.

 4. DownloadThreatReports : 

 >* This data connector will fetch the malware data and create the Link from which we can download Threat Reports. 

 5. RetryFailedIndicators : 

 >* This data connector will fetch failed indicators from failed indicators file and retry creating/updating Threat Intelligence indicators in Microsoft Sentinel. 





 For more details of REST APIs refer to the below documentations: 

 1. Cofense Intelligence API documentation: 

> https://www.threathq.com/docs/rest_api_reference.html 

 2. Microsoft Threat Intelligence Indicator documentation: 

> https://learn.microsoft.com/rest/api/securityinsights/preview/threat-intelligence-indicator 

 3. Microsoft Defender for Endpoints Indicator documentation: 

> https://learn.microsoft.com/microsoft-365/security/defender-endpoint/ti-indicator?view=o365-worldwide

| | |
|--------------------------|---|
| **Tables Ingested** | `Malware_Data_CL` |
| | `ThreatIntelligenceIndicator` |
| **Connector Definition Files** | [CofenseIntelligence_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CofenseIntelligence/Data%20Connectors/CofenseIntelligenceDataConnector/CofenseIntelligence_API_FunctionApp.json) |

[→ View full connector details](../connectors/cofenseintelligence.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Malware_Data_CL` | [Cofense Intelligence Threat Indicators Ingestion](../connectors/cofenseintelligence.md) |
| `ThreatIntelligenceIndicator` | [Cofense Intelligence Threat Indicators Ingestion](../connectors/cofenseintelligence.md) |

[← Back to Solutions Index](../solutions-index.md)
