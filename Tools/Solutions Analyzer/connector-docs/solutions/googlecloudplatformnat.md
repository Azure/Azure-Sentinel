# GoogleCloudPlatformNAT

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2025-05-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformNAT](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformNAT) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### Google Cloud Platform NAT (via Codeless Connector Framework)

**Publisher:** Microsoft

The Google Cloud Platform NAT data connector provides the capability to ingest Cloud NAT Audit logs and Cloud NAT Traffic logs into Microsoft Sentinel using the Compute Engine API. Refer the [Product overview](https://cloud.google.com/nat/docs/overview) document for more details.

**Tables Ingested:**

- `GCPNAT`
- `GCPNATAudit`

**Connector Definition Files:**

- [GCPNATLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformNAT/Data%20Connectors/GCPNATLogs_ccp/GCPNATLogs_ConnectorDefinition.json)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPNAT` | 1 connector(s) |
| `GCPNATAudit` | 1 connector(s) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n