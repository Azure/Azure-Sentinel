# AppServiceHTTPLogs

Reference for AppServiceHTTPLogs table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Azure Resources |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/appservicehttplogs) |

## Solutions (2)

This table is used by the following solutions:

- [Threat Intelligence](../solutions/threat-intelligence.md)
- [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md)

---

## Content Items Using This Table (2)

### Analytic Rules (2)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI map IP entity to AppServiceHTTPLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Analytic%20Rules/IPEntity_AppServiceHTTPLogs.yaml)

**In solution [Threat Intelligence (NEW)](../solutions/threat-intelligence-%28new%29.md):**
- [TI map IP entity to AppServiceHTTPLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence%20%28NEW%29/Analytic%20Rules/IPEntity_AppServiceHTTPLogs.yaml)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.web/sites`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
