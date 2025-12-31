# Infoblox SOC Insights

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Infoblox |
| **Support Tier** | Partner |
| **Support Link** | [https://support.infoblox.com/](https://support.infoblox.com/) |
| **Categories** | domains |
| **First Published** | 2024-03-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights) |

## Data Connectors

This solution provides **3 data connector(s)**:

- [[Deprecated] Infoblox SOC Insight Data Connector via AMA](../connectors/infobloxsocinsightsdataconnector-ama.md)
- [Infoblox SOC Insight Data Connector via REST API](../connectors/infobloxsocinsightsdataconnector-api.md)
- [[Deprecated] Infoblox SOC Insight Data Connector via Legacy Agent](../connectors/infobloxsocinsightsdataconnector-legacy.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Infoblox SOC Insight Data Connector via AMA](../connectors/infobloxsocinsightsdataconnector-ama.md), [[Deprecated] Infoblox SOC Insight Data Connector via Legacy Agent](../connectors/infobloxsocinsightsdataconnector-legacy.md) | Analytics |
| [`incidents`](../tables/incidents.md) | - | Workbooks |

### Internal Tables

The following **7 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`InfobloxInsightAssets_CL`](../tables/infobloxinsightassets-cl.md) | - | Playbooks (writes), Workbooks |
| [`InfobloxInsightComments_CL`](../tables/infobloxinsightcomments-cl.md) | - | Playbooks (writes), Workbooks |
| [`InfobloxInsightEvents_CL`](../tables/infobloxinsightevents-cl.md) | - | Playbooks (writes), Workbooks |
| [`InfobloxInsightIndicators_CL`](../tables/infobloxinsightindicators-cl.md) | - | Playbooks (writes), Workbooks |
| [`InfobloxInsight_CL`](../tables/infobloxinsight-cl.md) | [Infoblox SOC Insight Data Connector via REST API](../connectors/infobloxsocinsightsdataconnector-api.md) | Analytics, Playbooks (writes), Workbooks |
| [`SecurityAlert`](../tables/securityalert.md) | - | Workbooks |
| [`SecurityIncident`](../tables/securityincident.md) | - | Workbooks |

## Content Items

This solution includes **12 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 6 |
| Playbooks | 3 |
| Analytic Rules | 2 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Infoblox - SOC Insight Detected - API Source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights/Analytic%20Rules/Infoblox-SOCInsightDetected-APISource.yaml) | Medium | Impact | *Internal use:*<br>[`InfobloxInsight_CL`](../tables/infobloxinsight-cl.md) |
| [Infoblox - SOC Insight Detected - CDC Source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights/Analytic%20Rules/Infoblox-SOCInsightDetected-CDCSource.yaml) | Medium | Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [InfobloxSOCInsightsWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights/Workbooks/InfobloxSOCInsightsWorkbook.json) | [`incidents`](../tables/incidents.md)<br>*Internal use:*<br>[`InfobloxInsightAssets_CL`](../tables/infobloxinsightassets-cl.md)<br>[`InfobloxInsightComments_CL`](../tables/infobloxinsightcomments-cl.md)<br>[`InfobloxInsightEvents_CL`](../tables/infobloxinsightevents-cl.md)<br>[`InfobloxInsightIndicators_CL`](../tables/infobloxinsightindicators-cl.md)<br>[`InfobloxInsight_CL`](../tables/infobloxinsight-cl.md)<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Infoblox SOC Get Insight Details](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights/Playbooks/Infoblox-SOC-Get-Insight-Details/azuredeploy.json) | Leverages the Infoblox SOC Insights API to enrich a Microsoft Sentinel Incident triggered by an Info... | *Internal use:*<br>[`InfobloxInsightAssets_CL`](../tables/infobloxinsightassets-cl.md) *(write)*<br>[`InfobloxInsightComments_CL`](../tables/infobloxinsightcomments-cl.md) *(write)*<br>[`InfobloxInsightEvents_CL`](../tables/infobloxinsightevents-cl.md) *(write)*<br>[`InfobloxInsightIndicators_CL`](../tables/infobloxinsightindicators-cl.md) *(write)*<br>[`InfobloxInsight_CL`](../tables/infobloxinsight-cl.md) *(write)* |
| [Infoblox SOC Get Open Insights API](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights/Playbooks/Infoblox-SOC-Get-Open-Insights-API/azuredeploy.json) | Leverages the Infoblox SOC Insights API to ingest all Open/Active SOC Insights at time of run into t... | *Internal use:*<br>[`InfobloxInsight_CL`](../tables/infobloxinsight-cl.md) *(write)* |
| [Infoblox SOC Import Indicators TI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights/Playbooks/Infoblox-SOC-Import-Indicators-TI/azuredeploy.json) | Imports each Indicator of a Microsoft Sentinel Incident triggered by an Infoblox SOC Insight into th... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [InfobloxCDC_SOCInsights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights/Parsers/InfobloxCDC_SOCInsights.yaml) | - | - |
| [InfobloxInsight](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights/Parsers/InfobloxInsight.yaml) | - | - |
| [InfobloxInsightAssets](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights/Parsers/InfobloxInsightAssets.yaml) | - | - |
| [InfobloxInsightComments](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights/Parsers/InfobloxInsightComments.yaml) | - | - |
| [InfobloxInsightEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights/Parsers/InfobloxInsightEvents.yaml) | - | - |
| [InfobloxInsightIndicators](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights/Parsers/InfobloxInsightIndicators.yaml) | - | - |

## Release Notes

| **Version**   | **Date Modified**              | **Change History**                      |
|---------------|--------------------------------|-----------------------------------------|
| 3.0.2         | 28-06-2024                     | Deprecating data connectors  |
| 3.0.1         | 03-05-2024                     | Repackaged for parser issue fix on reinstall |
| 3.0.0         | 04-03-2024                     | Initial Solution Release                |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
