# Azure Storage Account

| | |
|----------|-------|
| **Connector ID** | `AzureStorageAccount` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AzureMetrics`](../tables-index.md#azuremetrics), [`StorageBlobLogs`](../tables-index.md#storagebloblogs), [`StorageFileLogs`](../tables-index.md#storagefilelogs), [`StorageQueueLogs`](../tables-index.md#storagequeuelogs), [`StorageTableLogs`](../tables-index.md#storagetablelogs) |
| **Used in Solutions** | [Azure Storage](../solutions/azure-storage.md) |
| **Connector Definition Files** | [AzureStorageAccount_CCP.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Storage/Data%20Connectors/AzureStorageAccount_CCP.JSON) |

Azure Storage account is a cloud solution for modern data storage scenarios. It contains all your data objects: blobs, files, queues, tables, and disks. This connector lets you stream Azure Storage accounts diagnostics logs into your Microsoft Sentinel workspace, allowing you to continuously monitor activity in all your instances, and detect malicious activity in your organization. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2220068&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **Policy**: owner role assigned for each policy assignment scope

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect your Azure Storage Account diagnostics logs into Sentinel.**

This connector uses a set of Azure Policies to apply a log-streaming configuration to a collection of instances, defined as a scope. Follow the instructions below to create and apply policies to all current and future instances. To get most out of the Storage Account Diagnostic logging from the Azure Storage Account, we recommend that you enable Diagnostic logging from all services within the Azure Storage Account - Blob, Queue, Table and File. Note, you may already have an active policy for this resource type.
**Stream diagnostics logs from your Azure Storage Account at scale**
**Launch the Azure Policy Assignment wizard and follow the steps.**

    >    1. In the **Basics** tab, click the button with the three dots under **Scope** to select your subscription.<br />2. In the **Parameters** tab, choose your Microsoft Sentinel workspace from the **Log Analytics workspace** drop-down list, and leave marked as "True" all the log categories you want to ingest.<br />3. To apply the policy on your existing resources, mark the **Create a remediation task** check box in the **Remediation** tab.</value>
    > 📋 **Additional Configuration Step**: This connector includes a configuration step of type `PolicyAssignment`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.
**Stream diagnostics logs from your Azure Storage Blob service at scale**
**Launch the Azure Policy Assignment wizard and follow the steps.**

    >    1. In the **Basics** tab, click the button with the three dots under **Scope** to select your subscription.<br />2. In the **Parameters** tab, choose your Microsoft Sentinel workspace from the **Log Analytics workspace** drop-down list, and leave marked as "True" all the log categories you want to ingest.<br />3. To apply the policy on your existing resources, mark the **Create a remediation task** check box in the **Remediation** tab.</value>
    > 📋 **Additional Configuration Step**: This connector includes a configuration step of type `PolicyAssignment`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.
**Stream diagnostics logs from your Azure Storage Queue service at scale**
**Launch the Azure Policy Assignment wizard and follow the steps.**

    >    1. In the **Basics** tab, click the button with the three dots under **Scope** to select your subscription.<br />2. In the **Parameters** tab, choose your Microsoft Sentinel workspace from the **Log Analytics workspace** drop-down list, and leave marked as "True" all the log categories you want to ingest.<br />3. To apply the policy on your existing resources, mark the **Create a remediation task** check box in the **Remediation** tab.</value>
    > 📋 **Additional Configuration Step**: This connector includes a configuration step of type `PolicyAssignment`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.
**Stream diagnostics logs from your Azure Storage Table service at scale**
**Launch the Azure Policy Assignment wizard and follow the steps.**

    >    1. In the **Basics** tab, click the button with the three dots under **Scope** to select your subscription.<br />2. In the **Parameters** tab, choose your Microsoft Sentinel workspace from the **Log Analytics workspace** drop-down list, and leave marked as "True" all the log categories you want to ingest.<br />3. To apply the policy on your existing resources, mark the **Create a remediation task** check box in the **Remediation** tab.</value>
    > 📋 **Additional Configuration Step**: This connector includes a configuration step of type `PolicyAssignment`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.
**Stream diagnostics logs from your Azure Storage File service at scale**
**Launch the Azure Policy Assignment wizard and follow the steps.**

    >    1. In the **Basics** tab, click the button with the three dots under **Scope** to select your subscription.<br />2. In the **Parameters** tab, choose your Microsoft Sentinel workspace from the **Log Analytics workspace** drop-down list, and leave marked as "True" all the log categories you want to ingest.<br />3. To apply the policy on your existing resources, mark the **Create a remediation task** check box in the **Remediation** tab.</value>
    > 📋 **Additional Configuration Step**: This connector includes a configuration step of type `PolicyAssignment`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
