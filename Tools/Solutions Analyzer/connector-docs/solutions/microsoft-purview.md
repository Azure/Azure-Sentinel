# Microsoft Purview

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-11-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Purview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Purview) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Microsoft Purview](../connectors/microsoftazurepurview.md)

**Publisher:** Microsoft

Connect to Microsoft Purview to enable data sensitivity enrichment of Microsoft Sentinel. Data classification and sensitivity label logs from Microsoft Purview scans can be ingested and visualized through workbooks, analytical rules, and more. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2224125&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| | |
|--------------------------|---|
| **Tables Ingested** | `PurviewDataSensitivityLogs` |
| **Connector Definition Files** | [MicrosoftPurview.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Purview/Data%20Connectors/MicrosoftPurview.json) |

[→ View full connector details](../connectors/microsoftazurepurview.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `PurviewDataSensitivityLogs` | [Microsoft Purview](../connectors/microsoftazurepurview.md) |

[← Back to Solutions Index](../solutions-index.md)
