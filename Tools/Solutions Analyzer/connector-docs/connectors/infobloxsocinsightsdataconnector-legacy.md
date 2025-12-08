# [Deprecated] Infoblox SOC Insight Data Connector via Legacy Agent

| | |
|----------|-------|
| **Connector ID** | `InfobloxSOCInsightsDataConnector_Legacy` |
| **Publisher** | Infoblox |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [Infoblox](../solutions/infoblox.md), [Infoblox SOC Insights](../solutions/infoblox-soc-insights.md) |
| **Connector Definition Files** | [InfobloxSOCInsightsDataConnector_Legacy.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Data%20Connectors/InfobloxSOCInsights/InfobloxSOCInsightsDataConnector_Legacy.json) |

The Infoblox SOC Insight Data Connector allows you to easily connect your Infoblox BloxOne SOC Insight data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log. 



This data connector ingests Infoblox SOC Insight CDC logs into your Log Analytics Workspace using the legacy Log Analytics agent.



**Microsoft recommends installation of Infoblox SOC Insight Data Connector via AMA Connector.** The legacy connector uses the Log Analytics agent which is about to be deprecated by **Aug 31, 2024,** and should only be installed where AMA is not supported.



 Using MMA and AMA on the same machine can cause log duplication and extra ingestion cost. [More details](https://learn.microsoft.com/en-us/azure/sentinel/ama-migrate).

[← Back to Connectors Index](../connectors-index.md)
