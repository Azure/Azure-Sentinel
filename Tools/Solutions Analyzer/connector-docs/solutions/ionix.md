# IONIX

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | IONIX |
| **Support Tier** | Partner |
| **Support Link** | [https://www.ionix.io/contact-us/](https://www.ionix.io/contact-us/) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IONIX](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IONIX) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [IONIX Security Logs](../connectors/cyberpionsecuritylogs.md)

**Publisher:** IONIX

The IONIX Security Logs data connector, ingests logs from the IONIX system directly into Sentinel. The connector allows users to visualize their data, create alerts and incidents and improve security investigations.

| | |
|--------------------------|---|
| **Tables Ingested** | `CyberpionActionItems_CL` |
| **Connector Definition Files** | [IONIXSecurityLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IONIX/Data%20Connectors/IONIXSecurityLogs.json) |

[→ View full connector details](../connectors/cyberpionsecuritylogs.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CyberpionActionItems_CL` | [IONIX Security Logs](../connectors/cyberpionsecuritylogs.md) |

[← Back to Solutions Index](../solutions-index.md)
