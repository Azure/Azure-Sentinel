# Palo Alto Prisma Cloud CWPP

## Solution Information

| | |
|------------------------|-------|
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

### [Palo Alto Prisma Cloud CWPP (using REST API)](../connectors/prismacloudcomputenativepoller.md)

**Publisher:** Microsoft

The [Palo Alto Prisma Cloud CWPP](https://prisma.pan.dev/api/cloud/cwpp/audits/#operation/get-audits-incidents) data connector allows you to connect to your Prisma Cloud CWPP instance and ingesting alerts into Microsoft Sentinel. The data connector is built on Microsoft Sentinel’s Codeless Connector Platform and uses the Prisma Cloud API to fetch security events and supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.

| | |
|--------------------------|---|
| **Tables Ingested** | `PrismaCloudCompute_CL` |
| **Connector Definition Files** | [PrismaCloudCompute_CLV2.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Prisma%20Cloud%20CWPP/Data%20Connectors/PrismaCloudCompute_CLV2.json) |

[→ View full connector details](../connectors/prismacloudcomputenativepoller.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `PrismaCloudCompute_CL` | [Palo Alto Prisma Cloud CWPP (using REST API)](../connectors/paloaltoprismacloudcwpp.md), [Palo Alto Prisma Cloud CWPP (using REST API)](../connectors/prismacloudcomputenativepoller.md) |

[← Back to Solutions Index](../solutions-index.md)
