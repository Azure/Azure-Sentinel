# [DEPRECATED] Palo Alto Prisma Cloud CSPM

| | |
|----------|-------|
| **Connector ID** | `PaloAltoPrismaCloud` |
| **Publisher** | Palo Alto |
| **Tables Ingested** | [`PaloAltoPrismaCloudAlert_CL`](../tables-index.md#paloaltoprismacloudalert_cl), [`PaloAltoPrismaCloudAudit_CL`](../tables-index.md#paloaltoprismacloudaudit_cl) |
| **Used in Solutions** | [PaloAltoPrismaCloud](../solutions/paloaltoprismacloud.md) |
| **Connector Definition Files** | [PrismaCloud_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoPrismaCloud/Data%20Connectors/PrismaCloud_API_FunctionApp.json) |

The Palo Alto Prisma Cloud CSPM data connector provides the capability to ingest [Prisma Cloud CSPM alerts](https://prisma.pan.dev/api/cloud/cspm/alerts#operation/get-alerts) and [audit logs](https://prisma.pan.dev/api/cloud/cspm/audit-logs#operation/rl-audit-logs) into Microsoft sentinel using the Prisma Cloud CSPM API. Refer to [Prisma Cloud CSPM API documentation](https://prisma.pan.dev/api/cloud/cspm) for more information.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[← Back to Connectors Index](../connectors-index.md)
