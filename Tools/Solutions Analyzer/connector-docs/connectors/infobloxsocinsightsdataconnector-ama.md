# [Recommended] Infoblox SOC Insight Data Connector via AMA

| | |
|----------|-------|
| **Connector ID** | `InfobloxSOCInsightsDataConnector_AMA` |
| **Publisher** | Infoblox |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [Infoblox](../solutions/infoblox.md), [Infoblox SOC Insights](../solutions/infoblox-soc-insights.md) |
| **Connector Definition Files** | [InfobloxSOCInsightsDataConnector_AMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Data%20Connectors/InfobloxSOCInsights/InfobloxSOCInsightsDataConnector_AMA.json) |

The Infoblox SOC Insight Data Connector allows you to easily connect your Infoblox BloxOne SOC Insight data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log. 



This data connector ingests Infoblox SOC Insight CDC logs into your Log Analytics Workspace using the new Azure Monitor Agent. Learn more about ingesting using the new Azure Monitor Agent [here](https://learn.microsoft.com/azure/sentinel/connect-cef-ama). **Microsoft recommends using this Data Connector.**

[← Back to Connectors Index](../connectors-index.md)
