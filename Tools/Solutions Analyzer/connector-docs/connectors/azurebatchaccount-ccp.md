# Azure Batch Account

| | |
|----------|-------|
| **Connector ID** | `AzureBatchAccount_CCP` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AzureDiagnostics`](../tables-index.md#azurediagnostics) |
| **Used in Solutions** | [Azure Batch Account](../solutions/azure-batch-account.md) |
| **Connector Definition Files** | [AzureBatchAccount_CCP.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Batch%20Account/Data%20Connectors/AzureBatchAccount_CCP.JSON) |

Azure Batch Account is a uniquely identified entity within the Batch service. Most Batch solutions use Azure Storage for storing resource files and output files, so each Batch account is usually associated with a corresponding storage account. This connector lets you stream your Azure Batch account diagnostics logs into Microsoft Sentinel, allowing you to continuously monitor activity. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2224103&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[← Back to Connectors Index](../connectors-index.md)
