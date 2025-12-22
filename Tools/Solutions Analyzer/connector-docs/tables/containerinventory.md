# ContainerInventory

Reference for ContainerInventory table in Azure Monitor Logs.

| | |
|----------|-------|
| **Table Name** | `ContainerInventory` |
| **Category** | Containers |
| **Solutions Using Table** | 1 |
| **Connectors Ingesting** | 1 |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/containerinventory) |

⚠️ **Note:** This table name is unique to specific connectors.

---

## Solutions (1)

This table is used by the following solutions:

- [Azure kubernetes Service](../solutions/azure-kubernetes-service.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Azure Kubernetes Service (AKS)](../connectors/azurekubernetes.md)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.containerservice/managedclusters`
- `<br>microsoft.kubernetes/connectedclusters`
- `<br>microsoft.hybridcontainerservice/provisionedclusters`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
