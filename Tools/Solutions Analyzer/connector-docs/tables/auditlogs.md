# AuditLogs

Reference for AuditLogs table in Azure Monitor Logs.

| | |
|----------|-------|
| **Table Name** | `AuditLogs` |
| **Category** | Azure Resources |
| **Solutions Using Table** | 1 |
| **Connectors Ingesting** | 1 |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/auditlogs) |

⚠️ **Note:** This table name is unique to specific connectors.

---

## Solutions (1)

This table is used by the following solutions:

- [Microsoft Entra ID](../solutions/microsoft-entra-id.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Microsoft Entra ID](../connectors/azureactivedirectory.md)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.azureadgraph/tenants`
- `<br>microsoft.graph/tenants`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
