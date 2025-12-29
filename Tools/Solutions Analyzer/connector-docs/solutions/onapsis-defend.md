# Onapsis Defend

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Onapsis |
| **Support Tier** | Partner |
| **Support Link** | [https://onapsis.com/support/](https://onapsis.com/support/) |
| **Categories** | domains |
| **First Published** | 2025-07-17 |
| **Last Updated** | 2025-07-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Onapsis%20Defend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Onapsis%20Defend) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Onapsis Defend Integration](../connectors/onapsis.md)

**Publisher:** Onapsis Platform

Onapsis Defend Integration is aimed at forwarding alerts and logs collected and detected by Onapsis Platform into Microsoft Sentinel SIEM

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Onapsis_Defend_CL` |
| **Connector Definition Files** | [Onapsis.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Onapsis%20Defend/Data%20Connectors/Onapsis.json) |

[→ View full connector details](../connectors/onapsis.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Onapsis_Defend_CL` | [Onapsis Defend Integration](../connectors/onapsis.md), [Onapsis Defend: Integrate Unmatched SAP Threat Detection & Intel with Microsoft Sentinel](../connectors/onapsis.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 21-11-2025                     | Updated schema and added new fields.        |
| 3.0.0       | 01-08-2025                     | Initial Solution Release.          		 |

[← Back to Solutions Index](../solutions-index.md)
