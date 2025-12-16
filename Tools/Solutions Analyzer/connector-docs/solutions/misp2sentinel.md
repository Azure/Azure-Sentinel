# MISP2Sentinel

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Community |
| **Support Tier** | Community |
| **Support Link** | [https://github.com/cudeso/misp2sentinel](https://github.com/cudeso/misp2sentinel) |
| **Categories** | domains,verticals |
| **First Published** | 2023-07-29 |
| **Last Updated** | 2023-07-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MISP2Sentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MISP2Sentinel) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [MISP2Sentinel](../connectors/misp2sentinelconnector.md)

**Publisher:** MISP project & cudeso.be

This solution installs the MISP2Sentinel connector that allows you to automatically push threat indicators from MISP to Microsoft Sentinel via the Upload Indicators REST API. After installing the solution, configure and enable this data connector by following guidance in Manage solution view.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Installation and setup instructions**

Use the documentation from this GitHub repository to install and configure the MISP to Microsoft Sentinel connector: 

https://github.com/cudeso/misp2sentinel

| | |
|--------------------------|---|
| **Tables Ingested** | `ThreatIntelligenceIndicator` |
| **Connector Definition Files** | [MISP2SentinelConnector_UploadIndicatorsAPI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MISP2Sentinel/Data%20Connectors/MISP2SentinelConnector_UploadIndicatorsAPI.json) |

[→ View full connector details](../connectors/misp2sentinelconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ThreatIntelligenceIndicator` | [MISP2Sentinel](../connectors/misp2sentinelconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
