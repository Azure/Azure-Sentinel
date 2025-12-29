# ASimDnsActivityLogs

Reference for ASimDnsActivityLogs table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Table Name** | `ASimDnsActivityLogs` |
| **Category** | Security |
| **Solutions Using Table** | 2 |
| **Connectors Ingesting** | 2 |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✓ Yes |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/asimdnsactivitylogs) |

⚠️ **Note:** This table name is unique to specific connectors.

---

## Solutions (2)

This table is used by the following solutions:

- [CrowdStrike Falcon Endpoint Protection](../solutions/crowdstrike-falcon-endpoint-protection.md)
- [Windows Server DNS](../solutions/windows-server-dns.md)

## Connectors (2)

This table is ingested by the following connectors:

- [Windows DNS Events via AMA](../connectors/asimdnsactivitylogs.md)
- [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.securityinsights/dnsnormalized`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
