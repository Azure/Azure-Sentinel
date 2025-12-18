# MISP2Sentinel

| | |
|----------|-------|
| **Connector ID** | `MISP2SentinelConnector` |
| **Publisher** | MISP project & cudeso.be |
| **Tables Ingested** | [`ThreatIntelligenceIndicator`](../tables-index.md#threatintelligenceindicator) |
| **Used in Solutions** | [MISP2Sentinel](../solutions/misp2sentinel.md) |
| **Connector Definition Files** | [MISP2SentinelConnector_UploadIndicatorsAPI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MISP2Sentinel/Data%20Connectors/MISP2SentinelConnector_UploadIndicatorsAPI.json) |

This solution installs the MISP2Sentinel connector that allows you to automatically push threat indicators from MISP to Microsoft Sentinel via the Upload Indicators REST API. After installing the solution, configure and enable this data connector by following guidance in Manage solution view.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Installation and setup instructions**

Use the documentation from this GitHub repository to install and configure the MISP to Microsoft Sentinel connector: 

https://github.com/cudeso/misp2sentinel

[← Back to Connectors Index](../connectors-index.md)
