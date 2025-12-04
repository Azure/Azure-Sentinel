# Beyond Security beSECURE

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Beyond Security |
| **Support Tier** | Partner |
| **Support Link** | [https://beyondsecurity.freshdesk.com/support/home](https://beyondsecurity.freshdesk.com/support/home) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Beyond%20Security%20beSECURE](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Beyond%20Security%20beSECURE) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Beyond Security beSECURE](../connectors/beyondsecuritybesecure.md)

**Publisher:** Beyond Security

The [Beyond Security beSECURE](https://beyondsecurity.com/) connector allows you to easily connect your Beyond Security beSECURE scan events, scan results and audit trail with Azure Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's network and improves your security operation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `beSECURE_Audit_CL` |
| | `beSECURE_ScanEvent_CL` |
| | `beSECURE_ScanResults_CL` |
| **Connector Definition Files** | [Beyond%20Security%20beSECURE.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Beyond%20Security%20beSECURE/Data%20Connectors/Beyond%20Security%20beSECURE.json) |

[→ View full connector details](../connectors/beyondsecuritybesecure.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `beSECURE_Audit_CL` | [Beyond Security beSECURE](../connectors/beyondsecuritybesecure.md) |
| `beSECURE_ScanEvent_CL` | [Beyond Security beSECURE](../connectors/beyondsecuritybesecure.md) |
| `beSECURE_ScanResults_CL` | [Beyond Security beSECURE](../connectors/beyondsecuritybesecure.md) |

[← Back to Solutions Index](../solutions-index.md)
