# WireData

Reference for WireData table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Security, Virtual Machines |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/wiredata) |

## Solutions (1)

This table is used by the following solutions:

- [Threat Intelligence](../solutions/threat-intelligence.md)

---

## Content Items Using This Table (1)

### Hunting Queries (1)

**In solution [Threat Intelligence](../solutions/threat-intelligence.md):**
- [TI Map File Entity to WireData Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Hunting%20Queries/FileEntity_WireData.yaml)

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
