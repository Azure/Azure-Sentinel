# Common Event Format

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Common%20Event%20Format](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Common%20Event%20Format) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Common Event Format (CEF)](../connectors/cef.md)

**Publisher:** Any

### [Common Event Format (CEF) via AMA](../connectors/cefama.md)

**Publisher:** Microsoft

Common Event Format (CEF) is an industry standard format on top of Syslog messages, used by many security vendors to allow event interoperability among different platforms. By connecting your CEF logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2223547&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

**Permissions:**

**Resource Provider Permissions:**
- **Workspace data sources** (Workspace): read and write permissions.

**Custom Permissions:**

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Enable data collection rule​**

>  CEF Events logs are collected only from **Linux** agents.
- Configure CefAma data connector

- **Create data collection rule**

**2. Run the following command to install and apply the CEF collector:**

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [CEF%20AMA.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Common%20Event%20Format/Data%20Connectors/CEF%20AMA.JSON) |

[→ View full connector details](../connectors/cefama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [Common Event Format (CEF)](../connectors/cef.md), [Common Event Format (CEF) via AMA](../connectors/cefama.md) |

[← Back to Solutions Index](../solutions-index.md)
