# ForescoutHostPropertyMonitor

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Forescout Technologies |
| **Support Tier** | Partner |
| **Support Link** | [https://www.forescout.com/support](https://www.forescout.com/support) |
| **Categories** | domains |
| **First Published** | 2022-06-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForescoutHostPropertyMonitor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForescoutHostPropertyMonitor) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Forescout Host Property Monitor](../connectors/forescouthostpropertymonitor.md)

**Publisher:** Forescout

The Forescout Host Property Monitor connector allows you to connect host/policy/compliance properties from Forescout platform with Microsoft Sentinel, to view, create custom incidents, and improve investigation. This gives you more insight into your organization network and improves your security operation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `ForescoutComplianceStatus_CL` |
| | `ForescoutHostProperties_CL` |
| | `ForescoutPolicyStatus_CL` |
| **Connector Definition Files** | [ForescoutHostPropertyMonitor.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForescoutHostPropertyMonitor/Data%20Connectors/ForescoutHostPropertyMonitor.json) |

[→ View full connector details](../connectors/forescouthostpropertymonitor.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ForescoutComplianceStatus_CL` | [Forescout Host Property Monitor](../connectors/forescouthostpropertymonitor.md) |
| `ForescoutHostProperties_CL` | [Forescout Host Property Monitor](../connectors/forescouthostpropertymonitor.md) |
| `ForescoutPolicyStatus_CL` | [Forescout Host Property Monitor](../connectors/forescouthostpropertymonitor.md) |

[← Back to Solutions Index](../solutions-index.md)
