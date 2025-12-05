# Azure Kubernetes Service (AKS)

| | |
|----------|-------|
| **Connector ID** | `AzureKubernetes` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AzureDiagnostics`](../tables-index.md#azurediagnostics), [`ContainerInventory`](../tables-index.md#containerinventory), [`KubeEvents`](../tables-index.md#kubeevents) |
| **Used in Solutions** | [Azure kubernetes Service](../solutions/azure-kubernetes-service.md) |
| **Connector Definition Files** | [AzureKubernetes.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20kubernetes%20Service/Data%20Connectors/AzureKubernetes.JSON) |

Azure Kubernetes Service (AKS) is an open-source, fully-managed container orchestration service that allows you to deploy, scale, and manage Docker containers and container-based applications in a cluster environment. This connector lets you stream your Azure Kubernetes Service (AKS) diagnostics logs into Microsoft Sentinel, allowing you to continuously monitor activity in all your instances. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2219762&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

[← Back to Connectors Index](../connectors-index.md)
