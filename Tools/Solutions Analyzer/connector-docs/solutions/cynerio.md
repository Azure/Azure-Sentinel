# Cynerio

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Cynerio |
| **Support Tier** | Partner |
| **Support Link** | [https://cynerio.com](https://cynerio.com) |
| **Categories** | domains |
| **First Published** | 2023-03-29 |
| **Last Updated** | 2023-03-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cynerio](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cynerio) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Cynerio Security Events](../connectors/cyneriosecurityevents.md)

**Publisher:** Cynerio

The [Cynerio](https://www.cynerio.com/) connector allows you to easily connect your Cynerio Security Events with Microsoft Sentinel, to view IDS Events. This gives you more insight into your organization network security posture and improves your security operation capabilities. 

| | |
|--------------------------|---|
| **Tables Ingested** | `CynerioEvent_CL` |
| **Connector Definition Files** | [Cynerio_Connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cynerio/Data%20Connectors/Cynerio_Connector.json) |

[→ View full connector details](../connectors/cyneriosecurityevents.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CynerioEvent_CL` | [Cynerio Security Events](../connectors/cyneriosecurityevents.md) |

[← Back to Solutions Index](../solutions-index.md)
