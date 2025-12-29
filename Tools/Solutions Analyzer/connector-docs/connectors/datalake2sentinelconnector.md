# Datalake2Sentinel

| | |
|----------|-------|
| **Connector ID** | `Datalake2SentinelConnector` |
| **Publisher** | Orange Cyberdefense |
| **Tables Ingested** | [`ThreatIntelligenceIndicator`](../tables-index.md#threatintelligenceindicator) |
| **Used in Solutions** | [Datalake2Sentinel](../solutions/datalake2sentinel.md) |
| **Connector Definition Files** | [Datalake2SentinelConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Datalake2Sentinel/Data%20Connectors/Datalake2SentinelConnector.json) |

This solution installs the Datalake2Sentinel connector which is built using the Codeless Connector Platform and allows you to automatically ingest threat intelligence indicators from **Datalake Orange Cyberdefense's CTI platform** into Microsoft Sentinel via the Upload Indicators REST API. After installing the solution, configure and enable this data connector by following guidance in Manage solution view.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Installation and setup instructions**

Use the documentation from this Github repository to install and configure the Datalake to Microsoft Sentinel connector. 

https://github.com/cert-orangecyberdefense/datalake2sentinel

[← Back to Connectors Index](../connectors-index.md)
