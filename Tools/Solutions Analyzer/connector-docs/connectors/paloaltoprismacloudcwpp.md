# Palo Alto Prisma Cloud CWPP (using REST API)

| | |
|----------|-------|
| **Connector ID** | `PaloAltoPrismaCloudCWPP` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`PrismaCloudCompute_CL`](../tables-index.md#prismacloudcompute_cl) |
| **Used in Solutions** | [Palo Alto Prisma Cloud CWPP](../solutions/palo-alto-prisma-cloud-cwpp.md) |
| **Connector Definition Files** | [connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Prisma%20Cloud%20CWPP/Data%20Connectors/PaloAltoPrismaCloudCWPP_ccp/connectorDefinition.json) |

The [Palo Alto Prisma Cloud CWPP](https://prisma.pan.dev/api/cloud/cwpp/audits/#operation/get-audits-incidents) data connector allows you to connect to your Palo Alto Prisma Cloud CWPP instance and ingesting alerts into Microsoft Sentinel. The data connector is built on Microsoft Sentinel's Codeless Connector Platform and uses the Prisma Cloud API to fetch security events and supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.
- **Keys** (Workspace): Read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Custom Permissions:**
- **PrismaCloudCompute API Key**: A Palo Alto Prisma Cloud CWPP Monitor API username and password is required. [See the documentation to learn more about PrismaCloudCompute SIEM API](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20Prisma%20Cloud%20CWPP/Data%20Connectors/readme.md).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Palo Alto Prisma Cloud CWPP Security Events to Microsoft Sentinel**

To enable the Palo Alto Prisma Cloud CWPP Security Events for Microsoft Sentinel, provide the required information below and click on Connect.
>
- **Path to console**: europe-west3.cloud.twistlock.com/{sasid}
- **Prisma Access Key (API)**: Prisma Access Key (API)
- **Secret**: (password field)
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
