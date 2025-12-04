# Azure Activity

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-04-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### Azure Activity

**Publisher:** Microsoft

Azure Activity Log is a subscription log that provides insight into subscription-level events that occur in Azure, including events from Azure Resource Manager operational data, service health events, write operations taken on the resources in your subscription, and the status of activities performed in Azure. For more information, see the [Microsoft Sentinel documentation ](https://go.microsoft.com/fwlink/p/?linkid=2219695&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

**Tables Ingested:**

- `AzureActivity`

**Connector Definition Files:**

- [AzureActivity.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Data%20Connectors/AzureActivity.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureActivity` | Azure Activity |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n