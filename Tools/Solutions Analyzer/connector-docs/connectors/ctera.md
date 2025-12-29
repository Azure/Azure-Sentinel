# CTERA Syslog

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `CTERA` |
| **Publisher** | CTERA Networks Ltd |
| **Used in Solutions** | [CTERA](../solutions/ctera.md) |
| **Collection Method** | Unknown |
| **Connector Definition Files** | [CTERA_Data_Connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Data%20Connectors/CTERA_Data_Connector.json) |

The CTERA Data Connector for Microsoft Sentinel offers monitoring and threat detection capabilities for your CTERA solution.

 It includes a workbook visualizing the sum of all operations per type, deletions, and denied access operations.

 It also provides analytic rules which detects ransomware incidents and alert you when a user is blocked due to suspicious ransomware activity.

 Additionally, it helps you identify critical patterns such as mass access denied events, mass deletions, and mass permission changes, enabling proactive threat management and response.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`Syslog`](../tables/syslog.md) | ✓ | ✓ |

> 💡 **Tip:** Tables with Ingestion API support allow data ingestion via the [Azure Monitor Data Collector API](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview), which also enables custom transformations during ingestion.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Step 1: Connect CTERA Platform to Syslog**

Set up your CTERA portal syslog connection and Edge-Filer Syslog connector

**2. Step 2: Install Azure Monitor Agent (AMA) on Syslog Server**

Install the Azure Monitor Agent (AMA) on your syslog server to enable data collection.

[← Back to Connectors Index](../connectors-index.md)
