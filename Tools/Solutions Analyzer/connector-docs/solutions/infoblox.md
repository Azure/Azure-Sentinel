# Infoblox

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Infoblox |
| **Support Tier** | Partner |
| **Support Link** | [https://support.infoblox.com/](https://support.infoblox.com/) |
| **Categories** | domains |
| **First Published** | 2024-07-15 |
| **Last Updated** | 2024-07-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox) |

## Data Connectors

This solution provides **4 data connector(s)**.

The Infoblox Cloud Data Connector allows you to easily connect your Infoblox data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_InfobloxCloudDataConnectorAma.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Data%20Connectors/InfobloxCEFDataConnector/template_InfobloxCloudDataConnectorAma.JSON) |

[→ View full connector details](../connectors/infobloxclouddataconnectorama.md)

### [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md)

**Publisher:** Infoblox

The Infoblox Data Connector allows you to easily connect your Infoblox TIDE data and Dossier data with Microsoft Sentinel. By connecting your data to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Failed_Range_To_Ingest_CL` |
| | `Infoblox_Failed_Indicators_CL` |
| | `dossier_atp_CL` |
| | `dossier_atp_threat_CL` |
| | `dossier_dns_CL` |
| | `dossier_geo_CL` |
| | `dossier_infoblox_web_cat_CL` |
| | `dossier_inforank_CL` |
| | `dossier_malware_analysis_v3_CL` |
| | `dossier_nameserver_CL` |
| | `dossier_nameserver_matches_CL` |
| | `dossier_ptr_CL` |
| | `dossier_rpz_feeds_CL` |
| | `dossier_rpz_feeds_records_CL` |
| | `dossier_threat_actor_CL` |
| | `dossier_tld_risk_CL` |
| | `dossier_whitelist_CL` |
| | `dossier_whois_CL` |
| **Connector Definition Files** | [Infoblox_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Data%20Connectors/InfobloxCloudDataConnector/Infoblox_API_FunctionApp.json) |

[→ View full connector details](../connectors/infobloxdataconnector.md)

### [[Recommended] Infoblox SOC Insight Data Connector via AMA](../connectors/infobloxsocinsightsdataconnector-ama.md)

**Publisher:** Infoblox

The Infoblox SOC Insight Data Connector allows you to easily connect your Infoblox BloxOne SOC Insight data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log. 



This data connector ingests Infoblox SOC Insight CDC logs into your Log Analytics Workspace using the new Azure Monitor Agent. Learn more about ingesting using the new Azure Monitor Agent [here](https://learn.microsoft.com/azure/sentinel/connect-cef-ama). **Microsoft recommends using this Data Connector.**

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [InfobloxSOCInsightsDataConnector_AMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Data%20Connectors/InfobloxSOCInsights/InfobloxSOCInsightsDataConnector_AMA.json) |

[→ View full connector details](../connectors/infobloxsocinsightsdataconnector-ama.md)

### [Infoblox SOC Insight Data Connector via REST API](../connectors/infobloxsocinsightsdataconnector-api.md)

**Publisher:** Infoblox

The Infoblox SOC Insight Data Connector allows you to easily connect your Infoblox BloxOne SOC Insight data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `InfobloxInsight_CL` |
| **Connector Definition Files** | [InfobloxSOCInsightsDataConnector_API.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Data%20Connectors/InfobloxSOCInsights/InfobloxSOCInsightsDataConnector_API.json) |

[→ View full connector details](../connectors/infobloxsocinsightsdataconnector-api.md)

### [[Deprecated] Infoblox SOC Insight Data Connector via Legacy Agent](../connectors/infobloxsocinsightsdataconnector-legacy.md)

**Publisher:** Infoblox

The Infoblox SOC Insight Data Connector allows you to easily connect your Infoblox BloxOne SOC Insight data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log. 



This data connector ingests Infoblox SOC Insight CDC logs into your Log Analytics Workspace using the legacy Log Analytics agent.



**Microsoft recommends installation of Infoblox SOC Insight Data Connector via AMA Connector.** The legacy connector uses the Log Analytics agent which is about to be deprecated by **Aug 31, 2024,** and should only be installed where AMA is not supported.



 Using MMA and AMA on the same machine can cause log duplication and extra ingestion cost. [More details](https://learn.microsoft.com/en-us/azure/sentinel/ama-migrate).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [InfobloxSOCInsightsDataConnector_Legacy.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Data%20Connectors/InfobloxSOCInsights/InfobloxSOCInsightsDataConnector_Legacy.json) |

[→ View full connector details](../connectors/infobloxsocinsightsdataconnector-legacy.md)

## Tables Reference

This solution ingests data into **20 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Infoblox SOC Insight Data Connector via Legacy Agent](../connectors/infobloxsocinsightsdataconnector-legacy.md), [[Recommended] Infoblox SOC Insight Data Connector via AMA](../connectors/infobloxsocinsightsdataconnector-ama.md) |
| `Failed_Range_To_Ingest_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `InfobloxInsight_CL` | [Infoblox SOC Insight Data Connector via REST API](../connectors/infobloxsocinsightsdataconnector-api.md) |
| `Infoblox_Failed_Indicators_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_atp_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_atp_threat_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_dns_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_geo_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_infoblox_web_cat_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_inforank_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_malware_analysis_v3_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_nameserver_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_nameserver_matches_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_ptr_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_rpz_feeds_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_rpz_feeds_records_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_threat_actor_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_tld_risk_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_whitelist_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |
| `dossier_whois_CL` | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
