# McAfee Network Security Platform

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-06-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20Network%20Security%20Platform](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20Network%20Security%20Platform) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] McAfee Network Security Platform](../connectors/mcafeensp.md)

**Publisher:** McAfee

The [McAfee® Network Security Platform](https://www.mcafee.com/enterprise/en-us/products/network-security-platform.html) data connector provides the capability to ingest [McAfee® Network Security Platform events](https://docs.mcafee.com/bundle/network-security-platform-10.1.x-integration-guide-unmanaged/page/GUID-8C706BE9-6AC9-4641-8A53-8910B51207D8.html) into Microsoft Sentinel. Refer to [McAfee® Network Security Platform](https://docs.mcafee.com/bundle/network-security-platform-10.1.x-integration-guide-unmanaged/page/GUID-F7D281EC-1CC9-4962-A7A3-5A9D9584670E.html) for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [McAfeeNSP.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20Network%20Security%20Platform/Data%20Connectors/McAfeeNSP.json) |

[→ View full connector details](../connectors/mcafeensp.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] McAfee Network Security Platform](../connectors/mcafeensp.md) |

[← Back to Solutions Index](../solutions-index.md)
