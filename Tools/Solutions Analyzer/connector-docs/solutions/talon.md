# Talon

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Talon Security |
| **Support Tier** | Partner |
| **Support Link** | [https://docs.console.talon-sec.com/](https://docs.console.talon-sec.com/) |
| **Categories** | domains |
| **First Published** | 2023-01-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Talon](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Talon) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Talon Insights](../connectors/talonlogs.md)

**Publisher:** Talon Security

The Talon Security Logs connector allows you to easily connect your Talon events and audit logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation.

| | |
|--------------------------|---|
| **Tables Ingested** | `Talon_CL` |
| **Connector Definition Files** | [TalonLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Talon/Data%20Connectors/TalonLogs.json) |

[→ View full connector details](../connectors/talonlogs.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Talon_CL` | [Talon Insights](../connectors/talonlogs.md) |

[← Back to Solutions Index](../solutions-index.md)
