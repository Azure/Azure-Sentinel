# Infoblox SOC Insight Data Connector via REST API

| | |
|----------|-------|
| **Connector ID** | `InfobloxSOCInsightsDataConnector_API` |
| **Publisher** | Infoblox |
| **Tables Ingested** | [`InfobloxInsight_CL`](../tables-index.md#infobloxinsight_cl) |
| **Used in Solutions** | [Infoblox](../solutions/infoblox.md), [Infoblox SOC Insights](../solutions/infoblox-soc-insights.md) |
| **Connector Definition Files** | [InfobloxSOCInsightsDataConnector_API.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Data%20Connectors/InfobloxSOCInsights/InfobloxSOCInsightsDataConnector_API.json) |

The Infoblox SOC Insight Data Connector allows you to easily connect your Infoblox BloxOne SOC Insight data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Workspace Keys**

In order to use the playbooks as part of this solution, find your **Workspace ID** and **Workspace Primary Key** below for your convenience.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Workspace Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**2. Parsers**

>This data connector depends on a parser based on a Kusto Function to work as expected called [**InfobloxInsight**](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20SOC%20Insights/Parsers/InfobloxInsight.yaml) which is deployed with the Microsoft Sentinel Solution.

**3. SOC Insights**

>This data connector assumes you have access to Infoblox BloxOne Threat Defense SOC Insights. You can find more information about SOC Insights [**here**](https://docs.infoblox.com/space/BloxOneThreatDefense/501514252/SOC+Insights).

**4. Follow the steps below to configure this data connector**
**1.  Generate an Infoblox API Key and copy it somewhere safe**

  In the [Infoblox Cloud Services Portal](https://csp.infoblox.com/atlas/app/welcome), generate an API Key and copy it somewhere safe to use in the next step. You can find instructions on how to create API keys [**here**](https://docs.infoblox.com/space/BloxOneThreatDefense/230394187/How+Do+I+Create+an+API+Key%3F).

  **2.  Configure the Infoblox-SOC-Get-Open-Insights-API playbook**

  Create and configure the **Infoblox-SOC-Get-Open-Insights-API** playbook which is deployed with this solution. Enter your Infoblox API key in the appropriate parameter when prompted.

[← Back to Connectors Index](../connectors-index.md)
