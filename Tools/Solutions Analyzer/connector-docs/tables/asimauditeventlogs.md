# ASimAuditEventLogs

Reference for ASimAuditEventLogs table in Azure Monitor Logs.

| | |
|----------|-------|
| **Table Name** | `ASimAuditEventLogs` |
| **Category** | Security |
| **Solutions Using Table** | 3 |
| **Connectors Ingesting** | 3 |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✓ Yes |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/asimauditeventlogs) |

⚠️ **Note:** This table name is unique to specific connectors.

---

## Solutions (3)

This table is used by the following solutions:

- [Cisco Meraki Events via REST API](../solutions/cisco-meraki-events-via-rest-api.md)
- [CrowdStrike Falcon Endpoint Protection](../solutions/crowdstrike-falcon-endpoint-protection.md)
- [Workday](../solutions/workday.md)

## Connectors (3)

This table is ingested by the following connectors:

- [Cisco Meraki (using REST API)](../connectors/ciscomerakimultirule.md)
- [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md)
- [Workday User Activity](../connectors/workdayccpdefinition.md)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.securityinsights/auditeventnormalized`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
