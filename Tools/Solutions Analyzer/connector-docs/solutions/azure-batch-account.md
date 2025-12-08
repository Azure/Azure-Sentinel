# Azure Batch Account

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Batch%20Account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Batch%20Account) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Azure Batch Account](../connectors/azurebatchaccount-ccp.md)

**Publisher:** Microsoft

Azure Batch Account is a uniquely identified entity within the Batch service. Most Batch solutions use Azure Storage for storing resource files and output files, so each Batch account is usually associated with a corresponding storage account. This connector lets you stream your Azure Batch account diagnostics logs into Microsoft Sentinel, allowing you to continuously monitor activity. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2224103&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| | |
|--------------------------|---|
| **Tables Ingested** | `AzureDiagnostics` |
| **Connector Definition Files** | [AzureBatchAccount_CCP.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Batch%20Account/Data%20Connectors/AzureBatchAccount_CCP.JSON) |

[→ View full connector details](../connectors/azurebatchaccount-ccp.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | [Azure Batch Account](../connectors/azurebatchaccount-ccp.md) |

[← Back to Solutions Index](../solutions-index.md)
