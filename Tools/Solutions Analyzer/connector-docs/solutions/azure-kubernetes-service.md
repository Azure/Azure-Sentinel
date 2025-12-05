# Azure kubernetes Service

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20kubernetes%20Service](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20kubernetes%20Service) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Azure Kubernetes Service (AKS)](../connectors/azurekubernetes.md)

**Publisher:** Microsoft

Azure Kubernetes Service (AKS) is an open-source, fully-managed container orchestration service that allows you to deploy, scale, and manage Docker containers and container-based applications in a cluster environment. This connector lets you stream your Azure Kubernetes Service (AKS) diagnostics logs into Microsoft Sentinel, allowing you to continuously monitor activity in all your instances. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2219762&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| | |
|--------------------------|---|
| **Tables Ingested** | `AzureDiagnostics` |
| | `ContainerInventory` |
| | `KubeEvents` |
| **Connector Definition Files** | [AzureKubernetes.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20kubernetes%20Service/Data%20Connectors/AzureKubernetes.JSON) |

[→ View full connector details](../connectors/azurekubernetes.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | [Azure Kubernetes Service (AKS)](../connectors/azurekubernetes.md) |
| `ContainerInventory` | [Azure Kubernetes Service (AKS)](../connectors/azurekubernetes.md) |
| `KubeEvents` | [Azure Kubernetes Service (AKS)](../connectors/azurekubernetes.md) |

[← Back to Solutions Index](../solutions-index.md)
