# ForgeRock Common Audit for CEF

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Forgerock |
| **Support Tier** | Partner |
| **Support Link** | [https://www.forgerock.com/support](https://www.forgerock.com/support) |
| **Categories** | domains |
| **First Published** | 2022-05-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForgeRock%20Common%20Audit%20for%20CEF](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForgeRock%20Common%20Audit%20for%20CEF) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] ForgeRock Identity Platform](../connectors/forgerock.md)

**Publisher:** ForgeRock Inc

The ForgeRock Identity Platform provides a single common auditing framework. Extract and aggregate log data across the entire platform with common audit (CAUD) event handlers and unique IDs so that it can be tracked holistically. Open and extensible, you can leverage audit logging and reporting capabilities for integration with Microsoft Sentinel via this CAUD for CEF connector.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [ForgeRock_CEF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForgeRock%20Common%20Audit%20for%20CEF/Data%20Connectors/ForgeRock_CEF.json) |

[→ View full connector details](../connectors/forgerock.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] ForgeRock Identity Platform](../connectors/forgerock.md) |

[← Back to Solutions Index](../solutions-index.md)
