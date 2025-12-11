# Palo Alto Prisma Cloud CSPM (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `PaloAltoPrismaCloudCSPMCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`PaloAltoPrismaCloudAlertV2_CL`](../tables-index.md#paloaltoprismacloudalertv2_cl), [`PaloAltoPrismaCloudAuditV2_CL`](../tables-index.md#paloaltoprismacloudauditv2_cl) |
| **Used in Solutions** | [PaloAltoPrismaCloud](../solutions/paloaltoprismacloud.md) |
| **Connector Definition Files** | [PaloAltoPrismaCloudCSPMLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Data%20Connectors/PrismaCloudCSPMLog_CCF/PaloAltoPrismaCloudCSPMLog_ConnectorDefinition.json) |

The Palo Alto Prisma Cloud CSPM data connector allows you to connect to your Palo Alto Prisma Cloud CSPM instance and ingesting Alerts (https://pan.dev/prisma-cloud/api/cspm/alerts/) & Audit Logs(https://pan.dev/prisma-cloud/api/cspm/audit-logs/) into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.
- **Keys** (Workspace): Read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Palo Alto Prisma Cloud CSPM Events to Microsoft Sentinel**

To get more information on how to obtain the Prisma Cloud Access Key, Secret Key, and Base URL, please refer to the[connector tutorial](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Data%20Connectors/Readme.md), provide the required information below and click on Connect.
>
- **Prisma Cloud Access Key**: Enter Access Key
- **Prisma Cloud Secret Key**: (password field)
- **Prisma Cloud Base URL**: https://api2.eu.prismacloud.io
- Click 'Connect' to establish connection
**Connector Management Interface**

This section is an interactive interface in the Microsoft Sentinel portal that allows you to manage your data collectors.

📊 **View Existing Collectors**: A management table displays all currently configured data collectors with the following information:
- **PaloAltoPrismaCloudCSPM Api Endpoints**

➕ **Add New Collector**: Click the "Add new collector" button to configure a new data collector (see configuration form below).

> 💡 **Portal-Only Feature**: This configuration interface is only available when viewing the connector in the Microsoft Sentinel portal. You cannot configure data collectors through this static documentation.

[← Back to Connectors Index](../connectors-index.md)
