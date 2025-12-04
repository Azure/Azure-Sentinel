# Dragos

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Dragos Inc |
| **Support Tier** | Partner |
| **Support Link** | [https://www.dragos.com](https://www.dragos.com) |
| **Categories** | domains |
| **First Published** | 2025-01-23 |
| **Last Updated** | 2025-01-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dragos](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dragos) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [ Dragos Notifications via Cloud Sitestore](../connectors/dragossitestoreccp.md)

**Publisher:** Dragos

The [Dragos Platform](https://www.dragos.com/) is the leading Industrial Cyber Security platform it offers a comprehensive Operational Technology (OT) cyber threat detection built by unrivaled industrial cybersecurity expertise. This solution enables Dragos Platform notification data to be viewed in Microsoft Sentinel so that security analysts are able to triage potential cyber security events occurring in their industrial environments.

| | |
|--------------------------|---|
| **Tables Ingested** | `DragosAlerts_CL` |
| **Connector Definition Files** | [dragosSitestoreDataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dragos/Data%20Connectors/DragosSiteStore_CCP/dragosSitestoreDataConnectorDefinition.json) |

[→ View full connector details](../connectors/dragossitestoreccp.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `DragosAlerts_CL` | [ Dragos Notifications via Cloud Sitestore](../connectors/dragossitestoreccp.md) |

[← Back to Solutions Index](../solutions-index.md)
