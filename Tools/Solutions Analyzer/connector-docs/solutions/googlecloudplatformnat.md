# GoogleCloudPlatformNAT

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2025-05-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformNAT](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformNAT) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Google Cloud Platform NAT (via Codeless Connector Framework)](../connectors/gcpnatlogsccpdefinition.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`GCPNAT`](../tables/gcpnat.md) | [Google Cloud Platform NAT (via Codeless Connector Framework)](../connectors/gcpnatlogsccpdefinition.md) | - |
| [`GCPNATAudit`](../tables/gcpnataudit.md) | [Google Cloud Platform NAT (via Codeless Connector Framework)](../connectors/gcpnatlogsccpdefinition.md) | - |

## Release Notes

**Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**                                                                         |
|------------|-------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.1      | 03-09-2025                    | Google Cloud Platform NAT **CCF Data Connector** moving to GA							 |
| 3.0.0      | 17-07-2025                    | Initial Solution Release. <br/> Added new **CCF Connector** - *GCPNATLogsCCPDefinition.*	 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
