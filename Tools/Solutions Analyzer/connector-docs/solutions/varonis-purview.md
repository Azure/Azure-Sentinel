# Varonis Purview

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Varonis |
| **Support Tier** | Partner |
| **Support Link** | [https://www.varonis.com/resources/support](https://www.varonis.com/resources/support) |
| **Categories** | domains |
| **First Published** | 2025-10-27 |
| **Last Updated** | 2025-10-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Varonis%20Purview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Varonis%20Purview) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Varonis Purview Push Connector](../connectors/varonispurviewpush.md)

**Publisher:** Varonis

The [Varonis Purview](https://www.varonis.com/) connector provides the capability to sync resources from Varonis to Microsoft Purview.

| | |
|--------------------------|---|
| **Tables Ingested** | `varonisresources_CL` |
| **Connector Definition Files** | [VaronisPurview_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Varonis%20Purview/Data%20Connectors/VaronisPurview_ccp/VaronisPurview_connectorDefinition.json) |

[→ View full connector details](../connectors/varonispurviewpush.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `varonisresources_CL` | [Varonis Purview Push Connector](../connectors/varonispurviewpush.md) |

[← Back to Solutions Index](../solutions-index.md)
