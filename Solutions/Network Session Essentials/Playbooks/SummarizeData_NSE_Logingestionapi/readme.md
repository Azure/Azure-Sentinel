# Network Session Essentials Solution Summarization Capability

This Logic App summarizes Network Session data into custom Log Analytics tables by using the Logs Ingestion API. This capability incurs additional cost.

## Summary

The playbook improves Network Session Essentials workbook and query performance by creating summarized data for key ASIM Network Session dimensions. It uses a data collection endpoint (DCE), data collection rule (DCR), and the playbook's managed identity to ingest data into V1 custom tables.

## V1 custom tables

The playbook creates the following tables. Use these V1 names in custom queries; existing non-V1 tables are not modified.

| Table | Summarized dimensions |
| --- | --- |
| `NetworkCustomAnalytics_ipV1_CL` | Source IP, destination IP, network direction, and device action. |
| `NetworkCustomAnalytics_source_portV1_CL` | Source port, network direction, and device action. |
| `NetworkCustomAnalytics_countryV1_CL` | Source country, destination country, device action, and network direction. |
| `NetworkCustomAnalyticsV1_CL` | Overall event result, network direction, device action, and event severity. |
| `NetworkCustomAnalytics_protocolV1_CL` | Network protocol, destination port, destination application, network direction, and device action. |
| `NetworkCustomAnalytics_sourceInfoV1_CL` | Event product and device hostname. |
| `NetworkCustomAnalytics_threatV1_CL` | Threat, threat category, event severity, and device action. |
| `NetworkCustomAnalytics_threat_iocV1_CL` | Source and destination IP addresses and hostnames. |
| `NetworkCustomAnalytics_ruleV1_CL` | Rule, network direction, and device action. |

Each table also includes `TimeGenerated`, `EventTime`, and `count_` for its aggregation window and event count.

## Deployment Instructions

1. Deploy the playbook by selecting the applicable button:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2F2e5433738eed60dd88d064d02e2795b607a316f1%2FSolutions%2FNetwork%2520Session%2520Essentials%2FPlaybooks%2FSummarizeData_NSE_Logingestionapi%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2F2e5433738eed60dd88d064d02e2795b607a316f1%2FSolutions%2FNetwork%2520Session%2520Essentials%2FPlaybooks%2FSummarizeData_NSE_Logingestionapi%2Fazuredeploy.json)

2. Deploy the playbook to a resource group in the same Azure region as the Log Analytics workspace.
3. Provide the required parameters:
   - **Playbook Name**: The default is `SummarizeData_NSE_Logingestionapi`.
   - **Log Analytics Name**: The Log Analytics workspace that contains the Network Session data.
   - **Resource Group Name** and **Subscription ID**: The workspace resource group and subscription.

The deployment creates the DCE, DCR, required custom tables, and grants the playbook managed identity the Monitoring Metrics Publisher role on the DCR.

## Post-Deployment Instructions

Authorize the Azure Monitor Logs API connection if prompted:

1. Open the Azure Monitor Logs API connection.
2. Select **Edit API connection**.
3. Select **Authorize**, sign in, and then save the connection.

The Logs Ingestion API uses the playbook's managed identity. No Azure Log Analytics Data Collector connection or workspace key is required.