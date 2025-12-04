# Azure Storage

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Storage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Storage) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Azure Storage Account](../connectors/azurestorageaccount.md)

**Publisher:** Microsoft

Azure Storage account is a cloud solution for modern data storage scenarios. It contains all your data objects: blobs, files, queues, tables, and disks. This connector lets you stream Azure Storage accounts diagnostics logs into your Microsoft Sentinel workspace, allowing you to continuously monitor activity in all your instances, and detect malicious activity in your organization. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2220068&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| | |
|--------------------------|---|
| **Tables Ingested** | `AzureMetrics` |
| | `StorageBlobLogs` |
| | `StorageFileLogs` |
| | `StorageQueueLogs` |
| | `StorageTableLogs` |
| **Connector Definition Files** | [AzureStorageAccount_CCP.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Storage/Data%20Connectors/AzureStorageAccount_CCP.JSON) |

[→ View full connector details](../connectors/azurestorageaccount.md)

## Tables Reference

This solution ingests data into **5 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureMetrics` | [Azure Storage Account](../connectors/azurestorageaccount.md) |
| `StorageBlobLogs` | [Azure Storage Account](../connectors/azurestorageaccount.md) |
| `StorageFileLogs` | [Azure Storage Account](../connectors/azurestorageaccount.md) |
| `StorageQueueLogs` | [Azure Storage Account](../connectors/azurestorageaccount.md) |
| `StorageTableLogs` | [Azure Storage Account](../connectors/azurestorageaccount.md) |

[← Back to Solutions Index](../solutions-index.md)
