# Palo Alto Prisma Cloud CWPP (using REST API)

| | |
|----------|-------|
| **Connector ID** | `PrismaCloudComputeNativePoller` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`PrismaCloudCompute_CL`](../tables-index.md#prismacloudcompute_cl) |
| **Used in Solutions** | [Palo Alto Prisma Cloud CWPP](../solutions/palo-alto-prisma-cloud-cwpp.md) |
| **Connector Definition Files** | [PrismaCloudCompute_CLV2.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Prisma%20Cloud%20CWPP/Data%20Connectors/PrismaCloudCompute_CLV2.json) |

The [Palo Alto Prisma Cloud CWPP](https://prisma.pan.dev/api/cloud/cwpp/audits/#operation/get-audits-incidents) data connector allows you to connect to your Prisma Cloud CWPP instance and ingesting alerts into Microsoft Sentinel. The data connector is built on Microsoft Sentinel’s Codeless Connector Platform and uses the Prisma Cloud API to fetch security events and supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.

[← Back to Connectors Index](../connectors-index.md)
