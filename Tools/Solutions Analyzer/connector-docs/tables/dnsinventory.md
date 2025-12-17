# DnsInventory

Reference for DnsInventory table in Azure Monitor Logs.

| | |
|----------|-------|
| **Table Name** | `DnsInventory` |
| **Category** | Network |
| **Solutions Using Table** | 1 |
| **Connectors Ingesting** | 1 |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/dnsinventory) |

⚠️ **Note:** This table name is unique to specific connectors.

---

## Solutions (1)

This table is used by the following solutions:

- [Windows Server DNS](../solutions/windows-server-dns.md)

## Connectors (1)

This table is ingested by the following connectors:

- [DNS](../connectors/dns.md)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.compute/virtualmachines`
- `<br>microsoft.conenctedvmwarevsphere/virtualmachines`
- `<br>microsoft.azurestackhci/virtualmachines`
- `<br>microsoft.scvmm/virtualmachines`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
