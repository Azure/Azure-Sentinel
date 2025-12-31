# DnsInventory

Reference for DnsInventory table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Network |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/dnsinventory) |

## Solutions (1)

This table is used by the following solutions:

- [Windows Server DNS](../solutions/windows-server-dns.md)

## Connectors (1)

This table is ingested by the following connectors:

- [DNS](../connectors/dns.md)

---

## Content Items Using This Table (1)

### Workbooks (1)

**In solution [Windows Server DNS](../solutions/windows-server-dns.md):**
- [Dns](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Server%20DNS/Workbooks/Dns.json)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.compute/virtualmachines`
- `microsoft.conenctedvmwarevsphere/virtualmachines`
- `microsoft.azurestackhci/virtualmachines`
- `microsoft.scvmm/virtualmachines`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
