# Azure Storage

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Storage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Storage) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Azure Storage Account](../connectors/azurestorageaccount.md)

## Tables Reference

This solution uses **5 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AzureMetrics`](../tables/azuremetrics.md) | [Azure Storage Account](../connectors/azurestorageaccount.md) | - |
| [`StorageBlobLogs`](../tables/storagebloblogs.md) | [Azure Storage Account](../connectors/azurestorageaccount.md) | - |
| [`StorageFileLogs`](../tables/storagefilelogs.md) | [Azure Storage Account](../connectors/azurestorageaccount.md) | - |
| [`StorageQueueLogs`](../tables/storagequeuelogs.md) | [Azure Storage Account](../connectors/azurestorageaccount.md) | - |
| [`StorageTableLogs`](../tables/storagetablelogs.md) | [Azure Storage Account](../connectors/azurestorageaccount.md) | - |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
