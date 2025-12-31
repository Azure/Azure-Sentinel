# Azure kubernetes Service

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20kubernetes%20Service](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20kubernetes%20Service) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Azure Kubernetes Service (AKS)](../connectors/azurekubernetes.md)

## Tables Reference

This solution uses **4 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | [Azure Kubernetes Service (AKS)](../connectors/azurekubernetes.md) | Hunting |
| [`ContainerInventory`](../tables/containerinventory.md) | [Azure Kubernetes Service (AKS)](../connectors/azurekubernetes.md) | - |
| [`KubeEvents`](../tables/kubeevents.md) | [Azure Kubernetes Service (AKS)](../connectors/azurekubernetes.md) | - |
| [`securityresources`](../tables/securityresources.md) | - | Workbooks |

### Internal Tables

The following **1 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | - | Workbooks |

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 2 |
| Workbooks | 1 |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Azure RBAC AKS created role details](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20kubernetes%20Service/Hunting%20Queries/AKS-Rbac.yaml) | Persistence | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Determine users with cluster admin role](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20kubernetes%20Service/Hunting%20Queries/AKS-clusterrolebinding.yaml) | Persistence | [`AzureDiagnostics`](../tables/azurediagnostics.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [AksSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20kubernetes%20Service/Workbooks/AksSecurity.json) | [`securityresources`](../tables/securityresources.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
