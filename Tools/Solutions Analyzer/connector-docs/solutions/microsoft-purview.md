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

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Microsoft Purview account Owner or Contributor role to set up Diagnostic Settings. Microsoft Contributor role with write permissions to enable data connector, view workbook, and create analytic rules.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Microsoft Purview to Microsoft Sentinel**

Within the Azure Portal, navigate to your Purview resource:
 1. In the search bar, search for **Purview accounts.**
 2. Select the specific account that you would like to be set up with Sentinel.

Inside your Microsoft Purview resource:
 3. Select **Diagnostic Settings.**
 4. Select **+ Add diagnostic setting.**
 5. In the **Diagnostic setting** blade:
   - Select the Log Category as **DataSensitivityLogEvent**.
   - Select **Send to Log Analytics**.
   - Chose the log destination workspace. This should be the same workspace that is used by **Microsoft Sentinel.**
  - Click **Save**.

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
