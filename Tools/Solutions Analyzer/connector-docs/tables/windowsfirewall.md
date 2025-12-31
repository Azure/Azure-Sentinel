# WindowsFirewall

Reference for WindowsFirewall table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Windows |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/windowsfirewall) |

## Solutions (1)

This table is used by the following solutions:

- [Windows Firewall](../solutions/windows-firewall.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Windows Firewall](../connectors/windowsfirewall.md)

---

## Content Items Using This Table (1)

### Workbooks (1)

**In solution [Windows Firewall](../solutions/windows-firewall.md):**
- [WindowsFirewall](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Firewall/Workbooks/WindowsFirewall.json)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.compute/virtualmachines`
- `microsoft.conenctedvmwarevsphere/virtualmachines`
- `microsoft.azurestackhci/virtualmachines`
- `microsoft.scvmm/virtualmachines`
- `microsoft.compute/virtualmachinescalesets`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
