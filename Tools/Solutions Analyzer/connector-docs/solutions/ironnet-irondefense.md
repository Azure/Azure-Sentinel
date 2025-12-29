# IronNet IronDefense

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IronNet%20IronDefense](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IronNet%20IronDefense) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [IronNet IronDefense](../connectors/ironnetirondefense.md)

**Publisher:** IronNet

The IronNet IronDefense connector enables ingest of IronDefense alerts, events, and IronDome notifications into Sentinel, enabling Sentinel to utilize IronDefense's behavioral analytics and the IronDome community to quickly identify threats in your enterprise network.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [IronNetIronDefense.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IronNet%20IronDefense/Data%20Connectors/IronNetIronDefense.json) |

[→ View full connector details](../connectors/ironnetirondefense.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [IronNet IronDefense](../connectors/ironnetirondefense.md) |

[← Back to Solutions Index](../solutions-index.md)
