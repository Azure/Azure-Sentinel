# Bitglass

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Bitglass](../connectors/bitglass.md)

**Publisher:** Bitglass

The [Bitglass](https://www.bitglass.com/) data connector provides the capability to retrieve security event logs of the Bitglass services and more events into Microsoft Sentinel through the REST API. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| | |
|--------------------------|---|
| **Tables Ingested** | `BitglassLogs_CL` |
| **Connector Definition Files** | [Bitglass_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Bitglass/Data%20Connectors/Bitglass_API_FunctionApp.json) |

[→ View full connector details](../connectors/bitglass.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `BitglassLogs_CL` | [Bitglass](../connectors/bitglass.md) |

[← Back to Solutions Index](../solutions-index.md)
