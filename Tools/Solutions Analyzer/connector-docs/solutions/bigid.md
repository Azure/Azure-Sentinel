# BigID

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | BigID |
| **Support Tier** | Partner |
| **Support Link** | [https://www.bigid.com/support](https://www.bigid.com/support) |
| **Categories** | domains |
| **First Published** | 2025-10-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BigID](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BigID) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [BigID DSPM connector](../connectors/bigiddspmlogsconnectordefinition.md)

**Publisher:** BigID

The [BigID DSPM](https://bigid.com/data-security-posture-management/) data connector provides the capability to ingest BigID DSPM cases with affected objects and datasource information into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `BigIDDSPMCatalog_CL` |
| **Connector Definition Files** | [BigIDDSPMLogs_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BigID/Data%20Connectors/BigIDDSPMLogs_ccp/BigIDDSPMLogs_connectorDefinition.json) |

[→ View full connector details](../connectors/bigiddspmlogsconnectordefinition.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `BigIDDSPMCatalog_CL` | [BigID DSPM connector](../connectors/bigiddspmlogsconnectordefinition.md) |

## Release Notes

**Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**                                                                         |
|------------|-------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.0      | 15-10-2025    | First version of a BigID DSPM CCF Connector. <br/> BigID DSPM CCF Connector now using JWT user token authentication |

[← Back to Solutions Index](../solutions-index.md)
