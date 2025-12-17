# Event

Reference for Event table in Azure Monitor Logs.

| | |
|----------|-------|
| **Table Name** | `Event` |
| **Category** | Security |
| **Solutions Using Table** | 3 |
| **Connectors Ingesting** | 5 |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/event) |

⚠️ **Note:** This table name is unique to specific connectors.

---

## Solutions (3)

This table is used by the following solutions:

- [ALC-WebCTRL](../solutions/alc-webctrl.md)
- [Microsoft Exchange Security - Exchange On-Premises](../solutions/microsoft-exchange-security---exchange-on-premises.md)
- [MimecastTIRegional](../solutions/mimecasttiregional.md)

## Connectors (5)

This table is ingested by the following connectors:

- [Automated Logic WebCTRL ](../connectors/automatedlogicwebctrl.md)
- [[Deprecated] Microsoft Exchange Logs and Events](../connectors/esi-exchangeadminauditlogevents.md)
- [Microsoft Exchange Admin Audit Logs by Event Logs](../connectors/esi-opt1exchangeadminauditlogsbyeventlogs.md)
- [Microsoft Exchange Logs and Events](../connectors/esi-opt2exchangeserverseventlogs.md)
- [Mimecast Intelligence for Microsoft - Microsoft Sentinel](../connectors/mimecasttiregionalconnectorazurefunctions.md)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.operationalinsights/workspaces`
- `<br>microsoft.compute/virtualmachines`
- `<br>microsoft.conenctedvmwarevsphere/virtualmachines`
- `<br>microsoft.azurestackhci/virtualmachines`
- `<br>microsoft.scvmm/virtualmachines`
- `<br>microsoft.compute/virtualmachinescalesets`
- `<br>microsoft.azurestackhci/clusters`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
