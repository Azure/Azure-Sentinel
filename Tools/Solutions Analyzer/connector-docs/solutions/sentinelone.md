# SentinelOne

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2024-11-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [SentinelOne](../connectors/sentinelone.md)

**Publisher:** SentinelOne

The [SentinelOne](https://www.sentinelone.com/) data connector provides the capability to ingest common SentinelOne server objects such as Threats, Agents, Applications, Activities, Policies, Groups, and more events into Microsoft Sentinel through the REST API. Refer to API documentation: `https://<SOneInstanceDomain>.sentinelone.net/api-doc/overview` for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SentinelOne_CL` |
| **Connector Definition Files** | [SentinelOne_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Data%20Connectors/SentinelOne_API_FunctionApp.json) |

[→ View full connector details](../connectors/sentinelone.md)

### [SentinelOne](../connectors/sentineloneccp.md)

**Publisher:** Microsoft

The [SentinelOne](https://usea1-nessat.sentinelone.net/api-doc/overview) data connector allows ingesting logs from the SentinelOne API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses the SentinelOne API to fetch logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table so that queries don't need to parse it again, thus resulting in better performance.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SentinelOneActivities_CL` |
| | `SentinelOneAgents_CL` |
| | `SentinelOneAlerts_CL` |
| | `SentinelOneGroups_CL` |
| | `SentinelOneThreats_CL` |
| **Connector Definition Files** | [connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SentinelOne/Data%20Connectors/SentinelOne_ccp/connectorDefinition.json) |

[→ View full connector details](../connectors/sentineloneccp.md)

## Tables Reference

This solution ingests data into **6 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SentinelOneActivities_CL` | [SentinelOne](../connectors/sentineloneccp.md) |
| `SentinelOneAgents_CL` | [SentinelOne](../connectors/sentineloneccp.md) |
| `SentinelOneAlerts_CL` | [SentinelOne](../connectors/sentineloneccp.md) |
| `SentinelOneGroups_CL` | [SentinelOne](../connectors/sentineloneccp.md) |
| `SentinelOneThreats_CL` | [SentinelOne](../connectors/sentineloneccp.md) |
| `SentinelOne_CL` | [SentinelOne](../connectors/sentinelone.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.6       | 10-02-2025                     | Advancing CCP **Data Connector** from Public preview to Global Availability.|
| 3.0.5       | 20-01-2025                     | Updated "Sentinel One - Agent uninstalled from multiple hosts" **Analytic Rule** with  ActivityType  |
| 3.0.4       | 15-01-2025                     | Added older Function app **Data Connector** again to SOlution until final deprecation of Function app happens  |
| 3.0.3       | 12-12-2024                     | Added new CCP **Data Connector** and Updated **Parser**  |
| 3.0.2       | 11-09-2024                     | Updated the python runtime version to 3.11 in **Data Connector** Function App  |
| 3.0.1       | 03-05-2024                     | Repackaged for **Parser** issue fix             |
| 3.0.0       | 28-07-2023                     | Bug fixes in API version.                   |

[← Back to Solutions Index](../solutions-index.md)
