# MarkLogicAudit

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-08-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MarkLogicAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MarkLogicAudit) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] MarkLogic Audit](../connectors/marklogic.md)

**Publisher:** MarkLogic

MarkLogic data connector provides the capability to ingest [MarkLogicAudit](https://www.marklogic.com/) logs into Microsoft Sentinel. Refer to [MarkLogic documentation](https://docs.marklogic.com/guide/getting-started) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `MarkLogicAudit_CL` |
| **Connector Definition Files** | [Connector_MarkLogicAudit.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MarkLogicAudit/Data%20Connectors/Connector_MarkLogicAudit.json) |

[→ View full connector details](../connectors/marklogic.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `MarkLogicAudit_CL` | [[Deprecated] MarkLogic Audit](../connectors/marklogic.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                          |
|-------------|--------------------------------|-------------------------------------------------------------|
| 3.0.1       | 02-01-2025                     | Removed Deprecated **Data connector**                       |
| 3.0.0       | 12-08-2024                     | Deprecating data connector                                  |

[← Back to Solutions Index](../solutions-index.md)
