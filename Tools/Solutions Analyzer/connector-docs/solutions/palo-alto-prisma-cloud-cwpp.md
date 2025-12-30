# Palo Alto Prisma Cloud CWPP

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-06-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Prisma%20Cloud%20CWPP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Prisma%20Cloud%20CWPP) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Palo Alto Prisma Cloud CWPP (using REST API)](../connectors/paloaltoprismacloudcwpp.md)

**Publisher:** Microsoft

The [Palo Alto Prisma Cloud CWPP](https://prisma.pan.dev/api/cloud/cwpp/audits/#operation/get-audits-incidents) data connector allows you to connect to your Palo Alto Prisma Cloud CWPP instance and ingesting alerts into Microsoft Sentinel. The data connector is built on Microsoft Sentinel's Codeless Connector Platform and uses the Prisma Cloud API to fetch security events and supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `PrismaCloudCompute_CL` |
| **Connector Definition Files** | [connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Prisma%20Cloud%20CWPP/Data%20Connectors/PaloAltoPrismaCloudCWPP_ccp/connectorDefinition.json) |

[→ View full connector details](../connectors/paloaltoprismacloudcwpp.md)

### [Palo Alto Prisma Cloud CWPP (using REST API)](../connectors/prismacloudcomputenativepoller.md)

**Publisher:** Microsoft

The [Palo Alto Prisma Cloud CWPP](https://prisma.pan.dev/api/cloud/cwpp/audits/#operation/get-audits-incidents) data connector allows you to connect to your Prisma Cloud CWPP instance and ingesting alerts into Microsoft Sentinel. The data connector is built on Microsoft Sentinel’s Codeless Connector Platform and uses the Prisma Cloud API to fetch security events and supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `PrismaCloudCompute_CL` |
| **Connector Definition Files** | [PrismaCloudCompute_CLV2.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Prisma%20Cloud%20CWPP/Data%20Connectors/PrismaCloudCompute_CLV2.json) |

[→ View full connector details](../connectors/prismacloudcomputenativepoller.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `PrismaCloudCompute_CL` | [Palo Alto Prisma Cloud CWPP (using REST API)](../connectors/paloaltoprismacloudcwpp.md), [Palo Alto Prisma Cloud CWPP (using REST API)](../connectors/prismacloudcomputenativepoller.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.3       | 03-01-2024                     |	Repackaged for _solutionVersion issue in resource            |
| 3.0.2       | 03-01-2024                     |	Updated package version and password as a securestring            |
| 3.0.1       | 30-11-2023                     |	Updated the data connector and its associated package             |
| 3.0.0       | 10-10-2023                     |	Added new files to support CCP CLV2 and its package               |

[← Back to Solutions Index](../solutions-index.md)
