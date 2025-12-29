# PaloAltoPrismaCloud

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-04-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[DEPRECATED] Palo Alto Prisma Cloud CSPM](../connectors/paloaltoprismacloud.md)

**Publisher:** Palo Alto

The Palo Alto Prisma Cloud CSPM data connector provides the capability to ingest [Prisma Cloud CSPM alerts](https://prisma.pan.dev/api/cloud/cspm/alerts#operation/get-alerts) and [audit logs](https://prisma.pan.dev/api/cloud/cspm/audit-logs#operation/rl-audit-logs) into Microsoft sentinel using the Prisma Cloud CSPM API. Refer to [Prisma Cloud CSPM API documentation](https://prisma.pan.dev/api/cloud/cspm) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `PaloAltoPrismaCloudAlert_CL` |
| | `PaloAltoPrismaCloudAudit_CL` |
| **Connector Definition Files** | [PrismaCloud_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Data%20Connectors/PrismaCloud_API_FunctionApp.json) |

[→ View full connector details](../connectors/paloaltoprismacloud.md)

### [Palo Alto Prisma Cloud CSPM (via Codeless Connector Framework)](../connectors/paloaltoprismacloudcspmccpdefinition.md)

**Publisher:** Microsoft

The Palo Alto Prisma Cloud CSPM data connector allows you to connect to your Palo Alto Prisma Cloud CSPM instance and ingesting Alerts (https://pan.dev/prisma-cloud/api/cspm/alerts/) & Audit Logs(https://pan.dev/prisma-cloud/api/cspm/audit-logs/) into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `PaloAltoPrismaCloudAlertV2_CL` |
| | `PaloAltoPrismaCloudAuditV2_CL` |
| **Connector Definition Files** | [PaloAltoPrismaCloudCSPMLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Data%20Connectors/PrismaCloudCSPMLog_CCF/PaloAltoPrismaCloudCSPMLog_ConnectorDefinition.json) |

[→ View full connector details](../connectors/paloaltoprismacloudcspmccpdefinition.md)

## Tables Reference

This solution ingests data into **4 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `PaloAltoPrismaCloudAlertV2_CL` | [Palo Alto Prisma Cloud CSPM (via Codeless Connector Framework)](../connectors/paloaltoprismacloudcspmccpdefinition.md) |
| `PaloAltoPrismaCloudAlert_CL` | [[DEPRECATED] Palo Alto Prisma Cloud CSPM](../connectors/paloaltoprismacloud.md) |
| `PaloAltoPrismaCloudAuditV2_CL` | [Palo Alto Prisma Cloud CSPM (via Codeless Connector Framework)](../connectors/paloaltoprismacloudcspmccpdefinition.md) |
| `PaloAltoPrismaCloudAudit_CL` | [[DEPRECATED] Palo Alto Prisma Cloud CSPM](../connectors/paloaltoprismacloud.md) |

[← Back to Solutions Index](../solutions-index.md)
