# ASimNetworkSessionLogs

Reference for ASimNetworkSessionLogs table in Azure Monitor Logs.

| | |
|----------|-------|
| **Table Name** | `ASimNetworkSessionLogs` |
| **Category** | Security |
| **Solutions Using Table** | 4 |
| **Connectors Ingesting** | 4 |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✓ Yes |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/asimnetworksessionlogs) |

⚠️ **Note:** This table name is unique to specific connectors.

---

## Solutions (4)

This table is used by the following solutions:

- [Cisco Meraki Events via REST API](../solutions/cisco-meraki-events-via-rest-api.md)
- [CrowdStrike Falcon Endpoint Protection](../solutions/crowdstrike-falcon-endpoint-protection.md)
- [VMware Carbon Black Cloud](../solutions/vmware-carbon-black-cloud.md)
- [Windows Firewall](../solutions/windows-firewall.md)

## Connectors (4)

This table is ingested by the following connectors:

- [Cisco Meraki (using REST API)](../connectors/ciscomerakimultirule.md)
- [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md)
- [Windows Firewall Events via AMA](../connectors/windowsfirewallama.md)
- [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.securityinsights/networksessionnormalized`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
