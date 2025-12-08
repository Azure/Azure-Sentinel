# Zimperium Mobile Threat Defense

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Zimperium |
| **Support Tier** | Partner |
| **Support Link** | [https://www.zimperium.com/support/](https://www.zimperium.com/support/) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zimperium%20Mobile%20Threat%20Defense](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zimperium%20Mobile%20Threat%20Defense) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Zimperium Mobile Threat Defense](../connectors/zimperiummtdalerts.md)

**Publisher:** Zimperium

Zimperium Mobile Threat Defense connector gives you the ability to connect the Zimperium threat log with Microsoft Sentinel to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's mobile threat landscape and enhances your security operation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `ZimperiumMitigationLog_CL` |
| | `ZimperiumThreatLog_CL` |
| **Connector Definition Files** | [Zimperium%20MTD%20Alerts.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zimperium%20Mobile%20Threat%20Defense/Data%20Connectors/Zimperium%20MTD%20Alerts.json) |

[→ View full connector details](../connectors/zimperiummtdalerts.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ZimperiumMitigationLog_CL` | [Zimperium Mobile Threat Defense](../connectors/zimperiummtdalerts.md) |
| `ZimperiumThreatLog_CL` | [Zimperium Mobile Threat Defense](../connectors/zimperiummtdalerts.md) |

[← Back to Solutions Index](../solutions-index.md)
