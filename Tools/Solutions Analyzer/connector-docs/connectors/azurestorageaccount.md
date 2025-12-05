# Azure Storage Account

| | |
|----------|-------|
| **Connector ID** | `AzureStorageAccount` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AzureMetrics`](../tables-index.md#azuremetrics), [`StorageBlobLogs`](../tables-index.md#storagebloblogs), [`StorageFileLogs`](../tables-index.md#storagefilelogs), [`StorageQueueLogs`](../tables-index.md#storagequeuelogs), [`StorageTableLogs`](../tables-index.md#storagetablelogs) |
| **Used in Solutions** | [Azure Storage](../solutions/azure-storage.md) |
| **Connector Definition Files** | [AzureStorageAccount_CCP.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Storage/Data%20Connectors/AzureStorageAccount_CCP.JSON) |

Azure Storage account is a cloud solution for modern data storage scenarios. It contains all your data objects: blobs, files, queues, tables, and disks. This connector lets you stream Azure Storage accounts diagnostics logs into your Microsoft Sentinel workspace, allowing you to continuously monitor activity in all your instances, and detect malicious activity in your organization. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2220068&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[← Back to Connectors Index](../connectors-index.md)
