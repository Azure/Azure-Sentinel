# Keeper Security

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Keeper Security |
| **Support Tier** | Partner |
| **Support Link** | [https://www.keepersecurity.com](https://www.keepersecurity.com) |
| **Categories** | domains |
| **First Published** | 2025-06-03 |
| **Last Updated** | 2025-06-03 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Keeper%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Keeper%20Security) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### Keeper Security Push Connector

**Publisher:** Keeper Security

The [Keeper Security](https://keepersecurity.com) connector provides the capability to read raw event data from Keeper Security in Microsoft Sentinel.

**Tables Ingested:**

- `KeeperSecurityEventNewLogs_CL`

**Connector Definition Files:**

- [KepperSecurity_Definition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Keeper%20Security/Data%20Connectors/KeeperSecurity_ccp/KepperSecurity_Definition.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `KeeperSecurityEventNewLogs_CL` | Keeper Security Push Connector |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n