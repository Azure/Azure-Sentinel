# MISP2Sentinel

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ThreatIntelligenceIndicator` |
| **Connector Definition Files** | [MISP2SentinelConnector_UploadIndicatorsAPI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MISP2Sentinel/Data%20Connectors/MISP2SentinelConnector_UploadIndicatorsAPI.json) |

[→ View full connector details](../connectors/misp2sentinelconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ThreatIntelligenceIndicator` | [MISP2Sentinel](../connectors/misp2sentinelconnector.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 29-07-2023                     | **Data Connector** Initial version of MISP2Sentinel with support for Upload Indicators API

[← Back to Solutions Index](../solutions-index.md)
