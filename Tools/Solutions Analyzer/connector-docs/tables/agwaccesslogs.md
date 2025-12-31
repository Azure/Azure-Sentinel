# AGWAccessLogs

Reference for AGWAccessLogs table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Audit, Azure Resources, Network |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/agwaccesslogs) |

## Solutions (1)

This table is used by the following solutions:

- [Azure Web Application Firewall (WAF)](../solutions/azure-web-application-firewall-%28waf%29.md)

---

## Content Items Using This Table (1)

### Analytic Rules (1)

**In solution [Azure Web Application Firewall (WAF)](../solutions/azure-web-application-firewall-%28waf%29.md):**
- [A potentially malicious web request was executed against a web server](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Web%20Application%20Firewall%20%28WAF%29/Analytic%20Rules/MaliciousWAFSessions.yaml)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.network/applicationgateways`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
