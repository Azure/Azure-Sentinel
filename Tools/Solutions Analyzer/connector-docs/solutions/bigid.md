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

This solution provides **1 data connector(s)**:

- [BigID DSPM connector](../connectors/bigiddspmlogsconnectordefinition.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`BigIDDSPMCatalog_CL`](../tables/bigiddspmcatalog-cl.md) | [BigID DSPM connector](../connectors/bigiddspmlogsconnectordefinition.md) | - |

## Release Notes

**Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**                                                                         |
|------------|-------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.0      | 15-10-2025    | First version of a BigID DSPM CCF Connector. <br/> BigID DSPM CCF Connector now using JWT user token authentication |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
