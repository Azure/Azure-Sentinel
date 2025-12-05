# GoogleCloudPlatformDNS

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-07-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[DEPRECATED] Google Cloud Platform DNS](../connectors/gcpdnsdataconnector.md)

**Publisher:** Google

### [Google Cloud Platform DNS (via Codeless Connector Framework)](../connectors/gcpdnslogsccpdefinition.md)

**Publisher:** Microsoft

The Google Cloud Platform DNS data connector provides the capability to ingest Cloud DNS Query logs and Cloud DNS Audit logs into Microsoft Sentinel using the Google Cloud DNS API. Refer to [Cloud DNS API](https://cloud.google.com/dns/docs/reference/rest/v1) documentation for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `GCPDNS` |
| **Connector Definition Files** | [GCPDNSLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Data%20Connectors/GCPDNSLog_CCP/GCPDNSLog_ConnectorDefinition.json) |

[→ View full connector details](../connectors/gcpdnslogsccpdefinition.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GCPDNS` | [Google Cloud Platform DNS (via Codeless Connector Framework)](../connectors/gcpdnslogsccpdefinition.md) |
| `GCP_DNS_CL` | [[DEPRECATED] Google Cloud Platform DNS](../connectors/gcpdnsdataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
