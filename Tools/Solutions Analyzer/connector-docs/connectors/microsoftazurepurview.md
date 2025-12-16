# Microsoft Purview

| | |
|----------|-------|
| **Connector ID** | `MicrosoftAzurePurview` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`PurviewDataSensitivityLogs`](../tables-index.md#purviewdatasensitivitylogs) |
| **Used in Solutions** | [Microsoft Purview](../solutions/microsoft-purview.md) |
| **Connector Definition Files** | [MicrosoftPurview.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Purview/Data%20Connectors/MicrosoftPurview.json) |

Connect to Microsoft Purview to enable data sensitivity enrichment of Microsoft Sentinel. Data classification and sensitivity label logs from Microsoft Purview scans can be ingested and visualized through workbooks, analytical rules, and more. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2224125&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Microsoft Purview account Owner or Contributor role to set up Diagnostic Settings. Microsoft Contributor role with write permissions to enable data connector, view workbook, and create analytic rules.

## Setup Instructions

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

[← Back to Connectors Index](../connectors-index.md)
