# Infoblox SOC Insights

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Infoblox |
| **Support Tier** | Partner |
| **Support Link** | [https://support.infoblox.com/](https://support.infoblox.com/) |
| **Categories** | domains |
| **First Published** | 2024-03-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights) |

## Data Connectors

This solution provides **3 data connector(s)**.

### [[Deprecated] Infoblox SOC Insight Data Connector via AMA](../connectors/infobloxsocinsightsdataconnector-ama.md)

**Publisher:** Infoblox

### [Infoblox SOC Insight Data Connector via REST API](../connectors/infobloxsocinsightsdataconnector-api.md)

**Publisher:** Infoblox

### [[Deprecated] Infoblox SOC Insight Data Connector via Legacy Agent](../connectors/infobloxsocinsightsdataconnector-legacy.md)

**Publisher:** Infoblox

The Infoblox SOC Insight Data Connector allows you to easily connect your Infoblox BloxOne SOC Insight data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log. 



This data connector ingests Infoblox SOC Insight CDC logs into your Log Analytics Workspace using the legacy Log Analytics agent.



**Microsoft recommends installation of Infoblox SOC Insight Data Connector via AMA Connector.** The legacy connector uses the Log Analytics agent which is about to be deprecated by **Aug 31, 2024,** and should only be installed where AMA is not supported.



 Using MMA and AMA on the same machine can cause log duplication and extra ingestion cost. [More details](https://learn.microsoft.com/en-us/azure/sentinel/ama-migrate).

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [InfobloxSOCInsightsDataConnector_Legacy.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights/Data%20Connectors/InfobloxSOCInsightsDataConnector_Legacy.json) |

[→ View full connector details](../connectors/infobloxsocinsightsdataconnector-legacy.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Infoblox SOC Insight Data Connector via AMA](../connectors/infobloxsocinsightsdataconnector-ama.md), [[Deprecated] Infoblox SOC Insight Data Connector via Legacy Agent](../connectors/infobloxsocinsightsdataconnector-legacy.md) |
| `InfobloxInsight_CL` | [Infoblox SOC Insight Data Connector via REST API](../connectors/infobloxsocinsightsdataconnector-api.md) |

[← Back to Solutions Index](../solutions-index.md)
